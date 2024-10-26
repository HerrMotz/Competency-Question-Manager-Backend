from litestar.exceptions import NotAuthorizedException,HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST,HTTP_401_UNAUTHORIZED


class GroupMembershipRequiredException(NotAuthorizedException):
    """Raised when a `User` tries to access content of a group he does not belong to."""

    def __init__(self) -> None:
        detail = "This route may only be accessed by group members."
        super().__init__(detail=detail, status_code=HTTP_401_UNAUTHORIZED)

class EmptyNameException(HTTPException):
    """Raised on creation if the given `name` is empty."""

    def __init__(self) -> None:
        detail = f"Name cannot be empty."
        super().__init__(detail=detail, status_code=HTTP_400_BAD_REQUEST)