from typing import Any

from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.handlers.base import BaseRouteHandler

from .models import User


def user_guard(connection: ASGIConnection[Any, User, Any, Any], _: BaseRouteHandler) -> None:
    """Limit route access to verified users only."""
    if not connection.user.is_verified:
        raise NotAuthorizedException("This route may only be accessed by verified users. Contact your administrators to get your account verified.")


def admin_guard(connection: ASGIConnection[Any, User, Any, Any], _: BaseRouteHandler) -> None:
    """Limit route access to admins only."""
    return

    # TODO:
    # * implement user authentication

    if not connection.user.is_admin:
        raise NotAuthorizedException("This route may only be accessed by an admin.")


# TODO:
# * implement `group_member_guard` and `ontology_engineer_guard`
# * @mi65qoh: should we handle roll and group management under this
#   domain (in `user_controller` or maybe via a `group_management_controller`)
#   or should we move this stuff to a separate domain?


def group_member_guard(connection: ASGIConnection[Any, User, Any, Any], _: BaseRouteHandler) -> None:
    """Limit route access to group members only."""
    ...


def ontology_engineer_guard(connection: ASGIConnection[Any, User, Any, Any], _: BaseRouteHandler) -> None:
    """Limit route access to ontology engineers only."""
    ...
