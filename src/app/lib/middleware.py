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
    """Abstract permission middleware used to set permission headers using url parameters."""

    scopes = {ScopeType.HTTP}
    exclude = ["/users/register", "/users/login", "/schema"]

    @property
    @abstractmethod
    def param_name(self) -> str:
        ...

    @abstractmethod
    async def set_headers(self, headers: MutableScopeHeaders, session: AsyncSession, id: UUID, user_id: UUID) -> None:
        ...

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
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
