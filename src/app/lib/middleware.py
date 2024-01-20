from abc import abstractmethod
from typing import Any
from uuid import UUID

from domain.accounts.models import User
from lib.orm import session
from lib.utils import get_path_param
from litestar.connection.base import ASGIConnection
from litestar.datastructures import MutableScopeHeaders
from litestar.enums import ScopeType
from litestar.middleware.base import AbstractMiddleware
from litestar.types import Message, Receive, Scope, Send
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractUserPermissionsMiddleware(AbstractMiddleware):
    """Abstract permission middleware used to set permission headers using url parameters.

    Defines a middleware that injects itself into the response pipeline when a certain url parameter
    of type `UUID` is present. If the middleware is triggered the `set_headers` hook is called
    to modify the responses headers before the request is send.

    Notes:
        * requires an authorized `User`
        * only supports `HTTP` responses
    """

    scopes = {ScopeType.HTTP}
    exclude = ["/users/register", "/users/login", "/schema"]

    @property
    @abstractmethod
    def param_name(self) -> str:
        """Defines the name of the url parameter looked up before execution."""
        ...

    @abstractmethod
    async def set_headers(self, headers: MutableScopeHeaders, session: AsyncSession, id: UUID, user_id: UUID) -> None:
        """Used to modify the responses headers based of the current `User` and the found parameter."""
        ...

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Wraps the response with this middleware."""

        async def send_wrapper(message: Message) -> None:
            if message["type"] != "http.response.start":
                return await send(message)

            connection: ASGIConnection[Any, User, Any, Any] = ASGIConnection(scope)
            if parameter := get_path_param(UUID, self.param_name, connection):
                headers = MutableScopeHeaders.from_message(message)
                async with session() as session_:
                    await self.set_headers(headers, session_, parameter, connection.user.id)

            return await send(message)

        await self.app(scope, receive, send_wrapper)
