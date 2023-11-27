from uuid import UUID, uuid4

from .authentication.exceptions import (
    InvalidPasswordFormatException,
    InvalidPasswordLengthException,
)
from .authentication.services import EncryptionService, PasswordHash
from .dtos import UserGetDTO, UserLoginDTO, UserRegisterDTO, UserUpdateDTO
from .exceptions import DelegateHTTPException, EmailInUseException, NameInUseException
from .models import User


class UserService:
    encryption_service = EncryptionService()
    mock_db: dict[UUID, User] = {}

    def __init__(self) -> None:
        # TODO: move this into the database setup once established
        self.mock_db = {
            user.id: user
            for user in [
                self._get_mock_user("Chiara", "HalloWelt123"),
                self._get_mock_user("Daniel", "HalloWelt123"),
                self._get_mock_user("Malte", "HalloWelt123"),
                self._get_mock_user("Admin", "HalloWelt123", True),
            ]
        }

    def _get_mock_user(self, name: str, initial_password: str, admin: bool = False) -> User:
        id = uuid4()
        password = self.encryption_service.hash_password(initial_password)
        return User(id, f"{name.lower()}@uni-jena.de", name, password.hash, password.salt, admin, True)

    def _encrypt_password(self, password: str) -> PasswordHash:
        """Encrypts a given password.

        :param password: Password to encrypt.
        :raises DelegateHTTPException: If the given password is malformed.
        :return: A hashed password.
        """
        try:
            return self.encryption_service.hash_password(password)
        except (InvalidPasswordFormatException, InvalidPasswordLengthException) as exception:
            raise DelegateHTTPException(exception)

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

    async def get_user_by_credentials(self, data: UserLoginDTO) -> User | None:
        """Gets a `User` by his login credentials.

        :param data: The `User's` credentials.
        :return: A matching `User` if any.
        """
        if users := [*filter(lambda user: user.email == data.email, self.mock_db.values())]:
            user = users[0]
            if user.password_hash == self.encryption_service.resolve_password(data.password, user.password_salt):
                return user

        return None

    async def update_user(self, user_id: UUID, data: UserUpdateDTO) -> UserGetDTO | None:
        """Updates a specific `User` by his `id` and the given data.

        :param user_id: The `Users` `id`.
        :param data: Any updates that should be applied to the `User`.
        :return: The updated `User` if found.
        """
        if user := self.mock_db.get(user_id, None):
            user.email = data.email if data.email else user.email
            user.name = data.name if data.name else user.name
            user.is_system_admin = data.is_system_admin if data.is_system_admin else user.is_system_admin
            user.is_verified = data.is_verified if data.is_verified else user.is_verified

            if data.password:
                password = self._encrypt_password(data.password)
                user.password_hash = password.hash
                user.password_salt = password.salt

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
        password = self._encrypt_password(data.password)
        user = User(uuid, data.email, data.name, password.hash, password.salt, False, False)
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


MOCK_USER_SERVICE = UserService()
