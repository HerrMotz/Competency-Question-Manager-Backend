from typing import Annotated, TypeVar
from uuid import UUID

from litestar import Controller, Response, delete, get, post, put
from litestar.enums import RequestEncodingType
from litestar.params import Body, Dependency
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from sqlalchemy.ext.asyncio import AsyncSession

from ..authentication.middleware import AuthenticationMiddleware
from ..authentication.services import EncryptionService
from ..dtos import (
    UserAccessDTO,
    UserGetDTO,
    UserLoginDTO,
    UserRegisterDTO,
    UserUpdateDTO,
)
from ..exceptions import (
    UnmatchedCredentialsException,
    UserNotFoundException,
    VerificationRequiredException,
)
from ..guards import system_admin_guard
from ..services import UserService

T = TypeVar("T")
JsonEncoded = Annotated[T, Body(media_type=RequestEncodingType.JSON)]
AuthenticationDependency = Annotated[AuthenticationMiddleware, Dependency(skip_validation=True)]


class UserController(Controller):
    path = "/users"
    tags = ["User"]

    @get("/")
    async def get_users_handler(self, session: AsyncSession) -> list[UserGetDTO]:
        """Gets alls `Users`."""
        return await UserService.get_users(session)

    @get("/{user_id:uuid}")
    async def get_user_handler(self, session: AsyncSession, user_id: UUID) -> UserGetDTO:
        """Gets a specific `User`."""
        if user := await UserService.get_user(session, user_id):
            return user
        raise UserNotFoundException(user_id)

    @put("/{user_id:uuid}", guards=[system_admin_guard], status_code=HTTP_200_OK)
    async def update_user_handler(
        self,
        session: AsyncSession,
        encryption: EncryptionService,
        user_id: UUID,
        data: JsonEncoded[UserUpdateDTO],
    ) -> UserGetDTO:
        """Updates a specific `User`."""
        if user := await UserService.update_user(session, encryption, user_id, data):
            return user
        raise UserNotFoundException(user_id)

    @delete("/{user_id:uuid}", guards=[system_admin_guard], status_code=HTTP_204_NO_CONTENT)
    async def delete_user_handler(self, session: AsyncSession, user_id: UUID) -> None:
        """Deletes a specific `User`."""
        if _ := await UserService.delete_user(session, user_id):
            return
        raise UserNotFoundException(user_id)

    @post("/register", status_code=HTTP_201_CREATED)
    async def register_user_handler(
        self,
        session: AsyncSession,
        encryption: EncryptionService,
        data: JsonEncoded[UserRegisterDTO],
    ) -> UserGetDTO:
        """Registers a new `User`."""
        return await UserService.add_user(session, encryption, data)

    @put("/verify/{user_id:uuid}", guards=[system_admin_guard], status_code=HTTP_200_OK)
    async def verify_user_handler(self, session: AsyncSession, user_id: UUID) -> UserGetDTO:
        """Verifies a specific `User`."""
        if user := await UserService.verify_user(session, user_id):
            return user
        raise UserNotFoundException(user_id)

    @post("/login", status_code=HTTP_200_OK)
    async def login_handler(
        self,
        authenticator: AuthenticationDependency,
        session: AsyncSession,
        encryption: EncryptionService,
        data: JsonEncoded[UserLoginDTO],
    ) -> Response[UserAccessDTO]:
        """Returns a valid authentication header given a matching set of credentials."""
        if user := await UserService.get_user_by_credentials(session, encryption, data):
            if user.is_verified:
                return authenticator.login(user)
            raise VerificationRequiredException()
        raise UnmatchedCredentialsException()
