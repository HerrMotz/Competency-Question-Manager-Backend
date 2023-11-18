from uuid import UUID, uuid4

from .dtos import UserGetDTO, UserRegisterDTO, UserUpdate0DTO
from .exceptions import EmailInUseException, NameInUseException
from .models import User


class UserService:
    mock_db: dict[UUID, User] = {}

    async def get_users(self) -> list[UserGetDTO]:
        """Gets all `Users` from the database.

        :return: A `list` of all `Users`.
        """
        return [UserGetDTO.from_dict(**user.__dict__) for user in self.mock_db.values()]

    async def get_user(self, user_id: UUID) -> UserGetDTO | None:
        """Gets a specific `User` by his `id`.

        :param user_id: The `Users` `id`.
        :return: The selected `User` if found.
        """
        if user := self.mock_db.get(user_id, None):
            return UserGetDTO.from_dict(**user.__dict__)
        return None

    async def update_user(self, user_id: UUID, data: UserUpdate0DTO) -> UserGetDTO | None:
        """Updates a specific `User` by his `id` and the given data.

        :param user_id: The `Users` `id`.
        :param data: Any updates that should be applied to the `User`.
        :return: The updated `User` if found.
        """
        if user := self.mock_db.get(user_id, None):
            user.email = data.email if data.email else user.email
            user.name = data.name if data.name else user.name
            user.password = data.password if data.password else user.password
            user.is_admin = data.is_admin if data.is_admin else user.is_admin
            user.is_verified = data.is_verified if data.is_verified else user.is_verified
            self.mock_db[user.id] = user
            return UserGetDTO.from_dict(**user.__dict__)
        return None

    async def delete_user(self, user_id: UUID) -> bool:
        """Deletes a specific `User` by his `id`.

        :param user_id: The `Users` `id`.
        :return: `True` if a `User` was removed else `False`.
        """
        user = self.mock_db.pop(user_id, None)
        return True if user else False

    async def add_user(self, data: UserRegisterDTO) -> UserGetDTO:
        """Add a new `User` to the database and returns him.

        Notes:
            * name and email validation will be handled by database constraints

        :param data: The parameters for the new `User`.
        :raises NameInUseException: If the given `name` is not unique.
        :raises EmailInUseException: If the given `email` is not unique.
        :return: The new `User` if created.
        """

        if any([user for user in self.mock_db.values() if user.name == data.name]):
            raise NameInUseException(data.name)

        if any([user for user in self.mock_db.values() if user.email == data.email]):
            raise EmailInUseException(data.email)

        uuid = uuid4()
        user = User(uuid, data.email, data.name, data.password, False, False)
        self.mock_db[uuid] = user
        return UserGetDTO.from_dict(**user.__dict__)

    async def verify_user(self, user_id: UUID) -> UserGetDTO | None:
        """Directly verifies a specific `User` (alternative to `add_user`).

        :param user_id: The `Users` `id`.
        :return: The updated `User` if found.
        """
        if user := self.mock_db.get(user_id, None):
            user.is_verified = True
            self.mock_db[user.id] = user
            return UserGetDTO.from_dict(**user.__dict__)
        return None
