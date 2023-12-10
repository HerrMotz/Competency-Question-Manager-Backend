from typing import Iterable
from uuid import UUID, uuid4

from litestar.background_tasks import BackgroundTask
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .authentication.exceptions import InvalidPasswordFormatException, InvalidPasswordLengthException
from .authentication.services import EncryptionService, PasswordHash
from .dtos import UserGetDTO, UserLoginDTO, UserRegisterDTO, UserUpdateDTO
from .exceptions import DelegateHTTPException, EmailInUseException, NameInUseException
from .models import User


class UserService:
    encryption_service = EncryptionService()

    def _encrypt_password(self, password: str) -> PasswordHash:
        """Encrypts a given password.

        :param session: An active database session.
        :param password: Password to encrypt.
        :raises DelegateHTTPException: If the given password is malformed.
        :return: A hashed password.
        """
        try:
            return self.encryption_service.hash_password(password)
        except (InvalidPasswordFormatException, InvalidPasswordLengthException) as exception:
            raise DelegateHTTPException(exception)

    async def get_users(self, session: AsyncSession) -> list[UserGetDTO]:
        """Gets all `Users` from the database.

        :param session: An active database session.
        :return: A `list` of all `Users`.
        """
        if users := await session.scalars(select(User)):
            return [UserGetDTO.model_validate(user) for user in users.all()]
        return []

    async def get_user(self, session: AsyncSession, user_id: UUID) -> UserGetDTO | None:
        """Gets a specific `User` by his `id`.

        :param session: An active database session.
        :param user_id: The `Users` `id`.
        :return: The selected `User` if found.
        """
        if user := await session.scalar(select(User).where(User.id == user_id)):
            return UserGetDTO.model_validate(user)
        return None

    async def get_user_by_credentials(self, session: AsyncSession, data: UserLoginDTO) -> User | None:
        """Gets a `User` by his login credentials.

        :param session: An active database session.
        :param data: The `User's` credentials.
        :return: A matching `User` if any.
        """
        if user := await session.scalar(select(User).where(User.email == data.email)):
            if user.password_hash == self.encryption_service.resolve_password(data.password, user.password_salt):
                return user
        return None

    async def update_user(self, session: AsyncSession, user_id: UUID, data: UserUpdateDTO) -> UserGetDTO | None:
        """Updates a specific `User` by his `id` and the given data.

        :param session: An active database session.
        :param user_id: The `Users` `id`.
        :param data: Any updates that should be applied to the `User`.
        :return: The updated `User` if found.
        """
        if user := await session.scalar(select(User).where(User.id == user_id)):
            user.email = data.email if data.email else user.email
            user.name = data.name if data.name else user.name
            user.is_system_admin = data.is_system_admin if data.is_system_admin else user.is_system_admin
            user.is_verified = data.is_verified if data.is_verified else user.is_verified

            if data.password:
                password = self._encrypt_password(data.password)
                user.password_hash = password.hash
                user.password_salt = password.salt

            return UserGetDTO.model_validate(user)
        return None

    async def delete_user(self, session: AsyncSession, user_id: UUID) -> bool:
        """Deletes a specific `User` by his `id`.

        :param session: An active database session.
        :param user_id: The `Users` `id`.
        :return: `True` if a `User` was removed else `False`.
        """
        if user := await session.scalar(select(User).where(User.id == user_id)):
            await session.delete(user)
        return True if user else False

    async def add_user(self, session: AsyncSession, data: UserRegisterDTO) -> UserGetDTO:
        """Add a new `User` to the database and returns him.

        Notes:
            * name and email validation will be handled by database constraints

        :param session: An active database session.
        :param data: The parameters for the new `User`.
        :raises NameInUseException: If the given `name` is not unique.
        :raises EmailInUseException: If the given `email` is not unique.
        :return: The new `User` if created.
        """
        if await session.scalar(select(User).where(User.name == data.name)):
            raise NameInUseException(data.name)

        if await session.scalar(select(User).where(User.email == data.email)):
            raise EmailInUseException(data.email)

        uuid = uuid4()
        password = self._encrypt_password(data.password)
        user = User(
            id=uuid,
            email=data.email,
            name=data.name,
            password_hash=password.hash,
            password_salt=password.salt,
            is_system_admin=False,
            is_verified=False,
        )
        session.add(user)
        return UserGetDTO.model_validate(user)

    async def verify_user(self, session: AsyncSession, user_id: UUID) -> UserGetDTO | None:
        """Directly verifies a specific `User` (alternative to `add_user`).

        :param session: An active database session.
        :param user_id: The `Users` `id`.
        :return: The updated `User` if found.
        """
        if user := await session.scalar(select(User).where(User.id == user_id)):
            user.is_verified = True
            return UserGetDTO.model_validate(user)
        return None

    @staticmethod
    async def get_system_users(session: AsyncSession, emails: Iterable[EmailStr]) -> tuple[Iterable[User], BackgroundTask | None]:
        mails = set(emails)

        users = await session.scalars(select(User).where(User.email.in_(mails)))
        non_users = mails - set(map(lambda user: user.email, users))
        invite_task = BackgroundTask(lambda: map(lambda email: ..., non_users)) if non_users else None

        # TODO: handle non registered users, dummy user -> send invite mail

        return users, invite_task


MOCK_USER_SERVICE = UserService()
