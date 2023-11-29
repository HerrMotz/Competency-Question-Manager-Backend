class InvalidPasswordLengthException(Exception):
    """Raised if a given password is to short."""

    def __init__(self, *args: object) -> None:
        message = "A valid password must contain at least 8 characters."
        super().__init__(message, *args)


class InvalidPasswordFormatException(Exception):
    """Raised if a given password is to weak."""

    def __init__(self, *args: object) -> None:
        message = "A valid password must contain at least one lower and one upper case character, and at least one digit."
        super().__init__(message, *args)
