from typing import Any

from litestar.connection import ASGIConnection
from litestar.handlers.base import BaseRouteHandler

from .exceptions import (
    SystemAdministratorRequiredException,
    VerificationRequiredException,
)
from .models import User


async def user_guard(connection: ASGIConnection[Any, User, Any, Any], _: BaseRouteHandler) -> None:
    """Limit route access to verified users only."""

    if not connection.user.is_verified:
        raise VerificationRequiredException()


async def system_admin_guard(connection: ASGIConnection[Any, User, Any, Any], _: BaseRouteHandler) -> None:
    """Limit route access to system admins only."""
    if not connection.user.is_system_admin:
        raise SystemAdministratorRequiredException()
