from typing import Annotated, TypeVar
from uuid import UUID

from litestar import Controller, delete, get, post, put
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from ..dtos import UserGetDTO, UserRegisterDTO, UserUpdate0DTO
from ..exceptions import UserNotFoundException
from ..guards import admin_guard
from ..services import UserService

T = TypeVar("T")
JsonEncoded = Annotated[T, Body(media_type=RequestEncodingType.JSON)]


class UserController(Controller):
    user_service = UserService()
    path = "/users"
    tags = ["User"]

    @get("/")
    async def get_users_handler(self) -> list[UserGetDTO]:
        """Gets alls `Users`."""
        return await self.user_service.get_users()

    @get("/{user_id:uuid}")
    async def get_user_handler(self, user_id: UUID) -> UserGetDTO:
        """Gets a specific `User`."""
        if user := await self.user_service.get_user(user_id):
            return user
        raise UserNotFoundException(user_id)

    @put("/{user_id:uuid}", guards=[admin_guard], status_code=HTTP_200_OK)
    async def update_user_handler(self, user_id: UUID, data: JsonEncoded[UserUpdate0DTO]) -> UserGetDTO:
        """Updates a specific `User`."""
        if user := await self.user_service.update_user(user_id, data):
            return user
        raise UserNotFoundException(user_id)

    @delete("/{user_id:uuid}", guards=[admin_guard], status_code=HTTP_204_NO_CONTENT)
    async def delete_user_handler(self, user_id: UUID) -> None:
        """Deletes a specific `User`."""
        if _ := await self.user_service.delete_user(user_id):
            return
        raise UserNotFoundException(user_id)

    @post("/register", status_code=HTTP_201_CREATED)
    async def register_user_handler(self, data: JsonEncoded[UserRegisterDTO]) -> UserGetDTO:
        """Registers a new `User`."""
        return await self.user_service.add_user(data)

    @put("/verify/{user_id:uuid}", guards=[admin_guard], status_code=HTTP_200_OK)
    async def verify_user_handler(self, user_id: UUID) -> UserGetDTO:
        """Verifies a specific `User`."""
        if user := await self.user_service.verify_user(user_id):
            return user
        raise UserNotFoundException(user_id)

    @post("/login", status_code=HTTP_200_OK)
    async def login_handler(self) -> None:
        """Not yet implemented."""
        ...

    @get("/logout", status_code=HTTP_200_OK)
    async def logout_handler(self) -> None:
        """Not yet implemented."""
        ...
