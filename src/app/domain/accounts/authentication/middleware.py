from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Callable
from uuid import UUID

from litestar import Response
from litestar.config.app import AppConfig
from litestar.connection import ASGIConnection
from litestar.contrib.jwt import JWTAuth, Token
from litestar.di import Provide

from ..dtos import UserGetDTO
from ..models import User
from ..services import MOCK_USER_SERVICE


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
        )
        object.__setattr__(self, "authenticator", authenticator)

    async def _get_user_from_token(self, token: Token, _: "ASGIConnection[Any, Any, Any, Any]") -> User | None:
        # TODO: replace mock db with real database
        user_id = UUID(token.sub)
        return MOCK_USER_SERVICE.mock_db.get(user_id, None)

    def login(self, user: User) -> Response[UserGetDTO]:
        """Handles `User` login and returns a `Response` with set headers.

        :param user: The `User` to login.
        :return: A `Response` with the appropriate headers.
        """
        ident = user.id.hex
        extra = {"email": user.email}
        body = UserGetDTO.from_dict(**user.__dict__)
        return self.authenticator.login(ident, token_extras=extra, response_body=body)

    @property
    def dependency(self) -> Provide:
        """Gets this middleware as dependency for litestar's dependency injection."""
        return Provide(lambda: self, sync_to_thread=False)

    @property
    def on_app_init(self) -> Callable[[AppConfig], AppConfig]:
        """Gets the jwt authenticator backend's initialization event."""
        return self.authenticator.on_app_init
