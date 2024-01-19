from typing import TypeVar
from uuid import UUID

from domain.groups.services import GroupService
from lib.middleware import AbstractUserPermissionsMiddleware
from litestar.datastructures import MutableScopeHeaders
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class UserGroupPermissionsMiddleware(AbstractUserPermissionsMiddleware):
    """Handles group permission headers when accessing group routes."""

    _headers = ["Permissions-Group-Member", "Permissions-Project-Manager"]

    @property
    def param_name(self) -> str:
        return "group_id"

    async def set_headers(self, headers: MutableScopeHeaders, session: AsyncSession, id: UUID, user_id: UUID) -> None:
        headers[self._headers[0]] = str(await GroupService.is_member(session, id, user_id))
        headers[self._headers[1]] = str(await GroupService.is_manager(session, id, user_id))
