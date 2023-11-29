import dataclasses
from uuid import UUID


@dataclasses.dataclass
class User:
    id: UUID
    email: str
    name: str
    password_hash: bytes
    password_salt: bytes
    is_system_admin: bool
    is_verified: bool
