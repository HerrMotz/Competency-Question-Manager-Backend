from typing import Annotated, Any, Sequence, TypeVar
from uuid import UUID

from domain.accounts.authentication.services import EncryptionService
from domain.accounts.models import User
from domain.consolidations.models import Consolidation
from domain.groups.models import Group
from litestar import Controller, delete, get, post, put
from litestar.connection.request import Request
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_404_NOT_FOUND
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .dtos import (
    ProjectCreateDTO,
    ProjectDetailDTO,
    ProjectDTO,
    ProjectUpdateDTO,
    ProjectUsersAddDTO,
    ProjectUsersRemoveDTO,
)
from .middleware import UserProjectPermissionsMiddleware
from .models import Project
from .services import ProjectService

T = TypeVar("T")
JsonEncoded = Annotated[T, Body(media_type=RequestEncodingType.JSON)]


class ProjectController(Controller):
    path = "/projects"
    tags = ["Project"]
    middleware = [UserProjectPermissionsMiddleware]

    default_options = [
        selectinload(Project.managers),
        selectinload(Project.engineers),
        selectinload(Project.groups).options(
            selectinload(Group.members),
            selectinload(Group.questions),
        ),
        selectinload(Project.consolidations).options(
            selectinload(Consolidation.engineer),
            selectinload(Consolidation.questions),
        ),
    ]

    @get("/", return_dto=ProjectDTO)
    async def get_projects_handler(self, session: AsyncSession) -> Sequence[Project]:
        return await ProjectService.get_projects(session, self.default_options)

    @get("/{project_id:uuid}", return_dto=ProjectDetailDTO)
    async def get_project_handler(self, session: AsyncSession, project_id: UUID) -> Project:
        return await ProjectService.get_project(session, project_id, self.default_options)

    @post("/", return_dto=ProjectDTO)
    async def create_project_handler(
        self,
        session: AsyncSession,
        encryption: EncryptionService,
        data: JsonEncoded[ProjectCreateDTO],
    ) -> Project:
        return await ProjectService.create(session, encryption, data, self.default_options)

    @put("/{project_id:uuid}", return_dto=ProjectDTO)
    async def update_project_handler(
        self,
        session: AsyncSession,
        project_id: UUID,
        data: JsonEncoded[ProjectUpdateDTO],
    ) -> Project:
        return await ProjectService.update(session, project_id, data, self.default_options)

    @delete("/{project_id:uuid}")
    async def delete_project_handler(self, session: AsyncSession, project_id: UUID) -> None:
        if await ProjectService.delete(session, project_id):
            return
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)  # TODO: raise explicit exception

    @put("/{project_id:uuid}/managers/add", return_dto=ProjectDTO)
    async def add_managers_handler(
        self,
        session: AsyncSession,
        encryption: EncryptionService,
        project_id: UUID,
        data: JsonEncoded[ProjectUsersAddDTO],
    ) -> Project:
        return await ProjectService.add_managers(session, encryption, project_id, data, self.default_options)

    @put("/{project_id:uuid}/managers/remove", return_dto=ProjectDTO)
    async def remove_managers_handler(
        self,
        session: AsyncSession,
        project_id: UUID,
        data: JsonEncoded[ProjectUsersRemoveDTO],
    ) -> Project:
        return await ProjectService.remove_managers(session, project_id, data, self.default_options)

    @put("/{project_id:uuid}/engineers/add", return_dto=ProjectDTO)
    async def add_engineers_handler(
        self,
        session: AsyncSession,
        encryption: EncryptionService,
        project_id: UUID,
        data: JsonEncoded[ProjectUsersAddDTO],
    ) -> Project:
        return await ProjectService.add_engineers(session, encryption, project_id, data, self.default_options)

    @put("/{project_id:uuid}/engineers/remove", return_dto=ProjectDTO)
    async def remove_engineers_handler(
        self,
        session: AsyncSession,
        project_id: UUID,
        data: JsonEncoded[ProjectUsersRemoveDTO],
    ) -> Project:
        return await ProjectService.remove_engineers(session, project_id, data, self.default_options)

    @get("/my_projects", summary="Gets all Projects you are a part of", return_dto=ProjectDTO)
    async def my_projects(self, request: Request[User, Any, Any], session: AsyncSession) -> Sequence[Project]:
        """Get all projects you are part of, meaning you are a member of any `Group` within one of these `Project`s."""
        return await ProjectService.my_projects(session, request.user.id, self.default_options)
