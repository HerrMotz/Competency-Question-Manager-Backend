from uuid import UUID

from domain.accounts.models import User
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase

from .orm import session as session_maker
from domain.questions.models import Question


class MockDataService:
    """Simple mock data service.

    Tries to insert mock data on application start up, ignores any errors.

    TODO: make this optional
    """

    mock_password = b"\xef\xb9\tG\xff\x997\x88\x82\x95\x13\x1c(\x98\x81\x0e\xe9\x1a\xb4\xf0\x97\x11\x1c\x88\xb7\xc7\xfc\xe6l\xfa!\x835/\x95\xf9$\x8e.\xc1\xe1[z\xb8\xa7|\x81\xdc-\x1bir\x80I\x08|\xa8\xa6=d\xef\xe6w\x17a\x9c\xf8\xb5\xa1\xa5\x9dEd\xd0Z\x03mb\xc7\t\x15j\x80\xfc\xbaK.\xe9\xe5\xca\xe7xu\xfb\xd8z\xd3\xb6\xed\x04\xbe\x08u\xab\xae[\xc9\x9b3\xd4h\xbed`l7H\xb1\xe77*,e\x91+?\x8c\x99"
    mock_salt = b"i\xf1\xc7g\xf9\xba\x16\xd4\x00V\xbe!\xcf\x1e3\xfb[\x98\x0e\x9a\x16A\x0e\xb9'B\x89\x06Y\x97Y\xec\x1b%\xd3\xef\xabR\x16\xd3M4\xc8\x18\xfb4\xaa\xf6\x93*\xf5\x0b\x9f\xcby\xbe\xd2\x9b\x17\x83g\x80\xfa\x80\xd2\x94\xa1\x05\xcb\x03\x11\x85\xe9\xfd\x94\xb6\xea\xe7N7\x1e\x10SC\xc8\xa3\xc9\x01\xbd\x8b\xa3\xd9\xc8o*\xd7\xbd\xb1\x91\x17\xba\xe7\x10b\xd2g\xcb7G\x15%\xden\xdd\x9d\xa7:\x14w\xa8\\\xe0v,\xdb\xcf\xc3L"

    mock_users = [
        User(
            id=UUID("0051e4f8-f64a-4d96-96a9-7e397205da52"),
            email="chiara@uni-jena.de",
            name="Chiara",
            password_hash=mock_password,
            password_salt=mock_salt,
            is_system_admin=False,
            is_verified=True,
        ),
        User(
            id=UUID("e0ca0b85-2960-4f47-8a1c-1acda6d13b87"),
            email="daniel@uni-jena.de",
            name="Daniel",
            password_hash=mock_password,
            password_salt=mock_salt,
            is_system_admin=False,
            is_verified=True,
        ),
        User(
            id=UUID("a3fbf0c3-35cb-4774-8eba-10bdd1cbfb0c"),
            email="malte@uni-jena.de",
            name="Malte",
            password_hash=mock_password,
            password_salt=mock_salt,
            is_system_admin=False,
            is_verified=True,
        ),
        User(
            id=UUID("a8693768-244b-4b87-9972-548034df1cc3"),
            email="admin@uni-jena.de",
            name="Admin",
            password_hash=mock_password,
            password_salt=mock_salt,
            is_system_admin=True,
            is_verified=True,
        ),
        Question(
            question = "How is it?",
            version = 1,
            author_id = UUID("a8693768-244b-4b87-9972-548034df1cc3")
        )
    ]

    mock_data: list[DeclarativeBase] = [*mock_users]

    async def _add_mock_model(self, model: DeclarativeBase) -> None:
        async with session_maker() as session:
            try:
                session.add(model)
                await session.commit()
            except IntegrityError:
                ...

    async def on_startup(self) -> None:
        _ = [await self._add_mock_model(model) for model in self.mock_data]
