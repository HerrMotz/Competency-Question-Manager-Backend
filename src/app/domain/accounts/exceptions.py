from uuid import UUID

from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND


class UserNotFoundException(HTTPException):
    def __init__(self, user_id: UUID) -> None:
        detail = f"No user with id '{user_id}' was found."
        super().__init__(detail=detail, status_code=HTTP_404_NOT_FOUND)


class NameInUseException(HTTPException):
    def __init__(self, name: str) -> None:
        detail = f"A user with the name '{name}' already exists."
        super().__init__(detail=detail, status_code=HTTP_400_BAD_REQUEST)


class EmailInUseException(HTTPException):
    def __init__(self, email: str) -> None:
        detail = f"A user with the email address '{email}' already exists."
        super().__init__(detail=detail, status_code=HTTP_400_BAD_REQUEST)
