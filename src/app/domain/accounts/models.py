import dataclasses
from uuid import UUID


@dataclasses.dataclass
class User:
    id: UUID
    email: str
    name: str
    password: str
    is_admin: bool
    is_verified: bool
