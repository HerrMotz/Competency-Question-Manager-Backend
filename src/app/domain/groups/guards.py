from typing import Any
from uuid import UUID

from domain.accounts.models import User
from domain.projects.exceptions import ProjectManagerRequiredException
from lib.orm import session
from lib.utils import get_path_param
from litestar.connection.base import ASGIConnection
from litestar.exceptions.http_exceptions import ImproperlyConfiguredException
from litestar.handlers.base import BaseRouteHandler

from .exceptions import GroupMembershipRequiredException
from .services import GroupService


async def group_member_guard(connection: ASGIConnection[Any, User, Any, Any], _: BaseRouteHandler) -> None:
    """Limit route access to group members only.

    Requires a `group_id: UUID` path parameter to be set.
    """
    if connection.user.is_system_admin:
        return

    if group_id := get_path_param(UUID, "group_id", connection):
        async with session() as session_:
            if await GroupService.is_member(session_, group_id, connection.user.id):
                return

        raise GroupMembershipRequiredException()
    raise ImproperlyConfiguredException()


async def project_manager_guard(connection: ASGIConnection[Any, User, Any, Any], _: BaseRouteHandler) -> None:
    """Limit route access to project managers only based of a selected group.

    Requires a `group_id: UUID` path parameter to be set.
    """
    if connection.user.is_system_admin:
        return

    if group_id := get_path_param(UUID, "group_id", connection):
        async with session() as session_:
            if await GroupService.is_manager(session_, group_id, connection.user.id):
                return

        raise ProjectManagerRequiredException()
    raise ImproperlyConfiguredException()
