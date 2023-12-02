from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from sqlalchemy import LargeBinary
from sqlalchemy.orm import Mapped, mapped_column


class User(UUIDAuditBase):
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[bytes] = mapped_column(LargeBinary(length=128))
    password_salt: Mapped[bytes] = mapped_column(LargeBinary(length=128))
    is_system_admin: Mapped[bool]
    is_verified: Mapped[bool]
