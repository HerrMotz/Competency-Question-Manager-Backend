from typing import Annotated, Sequence, TypeVar
from uuid import UUID

from domain.accounts.authentication.services import EncryptionService
from domain.consolidations.models import Consolidation
from domain.groups.models import Group
from litestar import Controller, delete, get, post, put
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
from .models import Project
from .services import ProjectService
from .middleware import UserProjectPermissionsMiddleware

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
        return await ProjectService.remove_managers(session, project_id, data)

    @put("/{project_id:uuid}/engineers/add", return_dto=ProjectDTO)
    async def add_engineers_handler(
        self,
        session: AsyncSession,
        encryption: EncryptionService,
        project_id: UUID,
        data: JsonEncoded[ProjectUsersAddDTO],
    ) -> Project:
        return await ProjectService.add_engineers(session, encryption, project_id, data)

    @put("/{project_id:uuid}/engineers/remove", return_dto=ProjectDTO)
    async def remove_engineers_handler(
        self,
        session: AsyncSession,
        project_id: UUID,
        data: JsonEncoded[ProjectUsersRemoveDTO],
    ) -> Project:
        return await ProjectService.remove_engineers(session, project_id, data)
