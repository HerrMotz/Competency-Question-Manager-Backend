from uuid import UUID

from domain.projects.services import ProjectService
from lib.middleware import AbstractUserPermissionsMiddleware
from litestar.datastructures import MutableScopeHeaders
from sqlalchemy.ext.asyncio import AsyncSession


class UserProjectPermissionsMiddleware(AbstractUserPermissionsMiddleware):
    """Handles project permission headers when accessing project routes."""

    _headers = ["Permissions-Project-Manager", "Permissions-Project-Engineer", "Permissions-Project-Member"]

    @property
    def param_name(self) -> str:
        return "project_id"

    async def set_headers(self, headers: MutableScopeHeaders, session: AsyncSession, id: UUID, user_id: UUID) -> None:
        headers[self._headers[0]] = str(await ProjectService.is_manager(session, id, user_id))
        headers[self._headers[1]] = str(await ProjectService.is_engineer(session, id, user_id))
        headers[self._headers[2]] = str(await ProjectService.is_member(session, id, user_id))
