# pyright: reportUnusedVariable=false

from typing import Any, Type, TypeVar
from uuid import UUID

from litestar.connection import ASGIConnection
from litestar.exceptions import ImproperlyConfiguredException
from litestar.handlers.base import BaseRouteHandler

from .exceptions import (
    GroupMembershipRequiredException,
    ProjectManagerRequiredException,
    ProjectMembershipRequiredException,
    SystemAdministratorRequiredException,
    VerificationRequiredException,
)
from .models import User

T = TypeVar("T")


def _get_path_param(_: Type[T], param: str, connection: ASGIConnection[Any, Any, Any, Any]) -> T | None:
    """Walruses can't write type hints and functions lack support for generics (just pre 3.12 things)."""
    return connection.path_params.get(param, None)


async def user_guard(connection: ASGIConnection[Any, User, Any, Any], _: BaseRouteHandler) -> None:
    """Limit route access to verified users only."""

    # TODO: user guard will be fulfilled by authentication middleware

    if not connection.user.is_verified:
        raise VerificationRequiredException()


async def system_admin_guard(connection: ASGIConnection[Any, User, Any, Any], _: BaseRouteHandler) -> None:
    """Limit route access to system admins only."""
    if not connection.user.is_system_admin:
        raise SystemAdministratorRequiredException()


async def project_manager_guard(connection: ASGIConnection[Any, User, Any, Any], _: BaseRouteHandler) -> None:
    """Limit route access to project managers only.

    Requires a `project_id: UUID` path parameter to be set.
    """

    if project_id := _get_path_param(UUID, "project_id", connection):
        ...
        # 1. get project
        # 2. return if user is project manager, else raise

        raise ProjectManagerRequiredException()
    raise ImproperlyConfiguredException()


# TODO:
# * implement `group_member_guard` and `ontology_engineer_guard`
# * @mi65qoh: should we handle roll and group management under this
#   domain (in `user_controller` or maybe via a `group_management_controller`)
#   or should we move this stuff to a separate domain?


# TODO: are roles hierarchial (i.e. sys admin can do anything an project manager can)?


async def project_member_guard(connection: ASGIConnection[Any, User, Any, Any], _: BaseRouteHandler) -> None:
    """Limit route access to project members (i.e. members of groups within a project) only.

    Requires a `project_id: UUID` path parameter to be set.
    """

    if project_id := _get_path_param(UUID, "project_id", connection):
        ...
        # 1. get project
        # 2. return if user is in any project group, else raise

        raise ProjectMembershipRequiredException()
    raise ImproperlyConfiguredException()


async def group_member_guard(connection: ASGIConnection[Any, User, Any, Any], _: BaseRouteHandler) -> None:
    """Limit route access to group members only.

    Requires a `project_id: UUID` and `group_id: UUID` path parameter to be set.
    """

    if project_id := _get_path_param(UUID, "project_id", connection):
        if group_id := _get_path_param(UUID, "group_id", connection):
            ...
            # 1. get project
            # 2. get group
            # (3.) validate that group is part of project
            # 4. return if user is in group, else raise

            raise GroupMembershipRequiredException()
    raise ImproperlyConfiguredException()


async def ontology_engineer_guard(connection: ASGIConnection[Any, User, Any, Any], _: BaseRouteHandler) -> None:
    """Limit route access to ontology engineers only."""
    ...
