from typing import Any
from uuid import UUID

from domain.accounts.models import User
from lib.orm import session
from lib.utils import get_path_param
from litestar.connection.base import ASGIConnection
from litestar.exceptions.http_exceptions import ImproperlyConfiguredException
from litestar.handlers.base import BaseRouteHandler

from .exceptions import GroupMembershipRequiredException
from .services import GroupService


async def group_member_guard(connection: ASGIConnection[Any, User, Any, Any], _: BaseRouteHandler) -> None:
    """Limit route access to group members only.

    Requires a `project_id: UUID` and `group_id: UUID` path parameter to be set.
    """

    if group_id := get_path_param(UUID, "group_id", connection):
        async with session() as session_:
            if await GroupService.is_member(session_, group_id, connection.user.id):
                return

        raise GroupMembershipRequiredException()
    raise ImproperlyConfiguredException()
