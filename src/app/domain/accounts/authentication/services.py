import hashlib
import os
import re
from dataclasses import dataclass, field
from typing import NamedTuple

from .exceptions import InvalidPasswordFormatException, InvalidPasswordLengthException

PasswordHash = NamedTuple("PasswordHash", [("hash", bytes), ("salt", bytes)])


@dataclass(frozen=True)
class EncryptionService:
    """Encrypts passwords using `hashlib.scrypt`.

    Notes:
        * passwords are required to have a length of at least 8 characters
        * passwords must contain at least one lower and one upper case character,
          and at least one digit
    """

    memory_cost_factor: int = 16_384
    block_size: int = 8
    parallelization_factor: int = 1

    salt_length: int = 128
    key_length: int = 128

    _min_length: int = field(init=False, default=8)
    _format_pattern: re.Pattern[str] = field(init=False, default_factory=lambda: re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$"))

    def _hash_password(self, password: bytes, salt: bytes) -> bytes:
        """Delegates to `hashlib.scrypt` using this service's parameters."""
        return hashlib.scrypt(
            password,
            salt=salt,
            n=self.memory_cost_factor,
            r=self.block_size,
            p=self.parallelization_factor,
            dklen=self.key_length,
        )

    def hash_password(self, password: str) -> PasswordHash:
        """Hash a `password` using `hashlib.scrypt`.

        :param password: The `password` to encrypt.
        :raises InvalidPasswordLengthException: If the given `password` has less than 8 characters.
        :raises InvalidPasswordFormatException: If the given `password` is to weak (see notes section).
        :return: The encrypted `password`.
        """
        if len(password) < self._min_length:
            raise InvalidPasswordLengthException()

        if not self._format_pattern.match(password):
            raise InvalidPasswordFormatException()

        salt = os.urandom(self.salt_length)
        password_hash = self._hash_password(password.encode(), salt)
        return PasswordHash(password_hash, salt)

    def resolve_password(self, password: str, salt: bytes) -> bytes:
        """Resolve a given `password` using the given `salt`.

        :param password: The `User's` `password`.
        :param salt: The `salt` used for the initial hash.
        :return: The resolved `password`.
        """
        return self._hash_password(password.encode(), salt)
