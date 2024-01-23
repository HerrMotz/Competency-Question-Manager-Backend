from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Callable

from lib.orm import session
from litestar import Response
from litestar.config.app import AppConfig
from litestar.connection import ASGIConnection
from litestar.contrib.jwt import JWTAuth, Token
from litestar.di import Provide
from sqlalchemy import select

from ..dtos import UserAccessDTO
from ..models import User


@dataclass(frozen=True)
class AuthenticationMiddleware:
    """Authentication using json web tokens and http headers."""

    secret: str
    header: str
    lifetime: int
    exclude: list[str] = field(default_factory=lambda: ["/users/register", "/users/login", "/schema"])
    authenticator: JWTAuth[User] = field(init=False)

    def __post_init__(self) -> None:
        authenticator = JWTAuth[User](
            auth_header=self.header,
            retrieve_user_handler=self._get_user_from_token,
            default_token_expiration=timedelta(hours=self.lifetime),
            token_secret=self.secret,
            exclude=self.exclude,
            exclude_http_methods=["HEAD"],
        )
        object.__setattr__(self, "authenticator", authenticator)

    async def _get_user_from_token(self, token: Token, _: "ASGIConnection[Any, Any, Any, Any]") -> User | None:
        async with session() as _session:
            if user := await _session.scalar(select(User).where(User.id == token.sub)):
                return user
        return None

    def login(self, user: User) -> Response[UserAccessDTO]:
        """Handles `User` login and returns a `Response` with set headers.

        :param user: The `User` to login.
        :return: A `Response` with the appropriate headers.
        """
        ident = user.id.hex
        extra = {"email": user.email}
        body = UserAccessDTO.model_validate(user)
        response = self.authenticator.login(ident, token_extras=extra, response_body=body)
        response.content.token = response.headers.get(self.header)
        return response

    @property
    def dependency(self) -> Provide:
        """Gets this middleware as dependency for litestar's dependency injection."""
        return Provide(lambda: self, sync_to_thread=False)

    @property
    def on_app_init(self) -> Callable[[AppConfig], AppConfig]:
        """Gets the jwt authenticator backend's initialization event."""
        return self.authenticator.on_app_init
