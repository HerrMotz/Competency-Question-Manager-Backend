from typing import Annotated, Sequence, TypeVar
from uuid import UUID

from domain.accounts.authentication.services import EncryptionService
from domain.groups.models import Group
from domain.projects.middleware import UserProjectPermissionsMiddleware
from domain.questions.models import Question
from litestar import Controller, delete, get, post, put
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_404_NOT_FOUND
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .dtos import (
    GroupCreateDTO,
    GroupDetailDTO,
    GroupDTO,
    GroupUpdateDTO,
    GroupUsersAddDTO,
    GroupUsersRemoveDTO,
)
from .middleware import UserGroupPermissionsMiddleware
from .models import Group
from .services import GroupService

T = TypeVar("T")
JsonEncoded = Annotated[T, Body(media_type=RequestEncodingType.JSON)]


class GroupController(Controller):
    path = "/groups"
    tags = ["Groups"]
    middleware = [UserGroupPermissionsMiddleware, UserProjectPermissionsMiddleware]

    default_options = [
        selectinload(Group.members),
        selectinload(Group.project),
        selectinload(Group.questions).options(
            selectinload(Question.author),
            selectinload(Question.ratings),
        ),
    ]

    @get("/", return_dto=GroupDTO)
    async def get_groups_handler(self, session: AsyncSession) -> Sequence[Group]:
        """Gets all `Group`s."""
        return await GroupService.get_groups(session, options=self.default_options)

    @get("/{project_id:uuid}", return_dto=GroupDTO)
    async def get_project_groups_handler(self, session: AsyncSession, project_id: UUID) -> Sequence[Group]:
        """Gets all `Group`s. belonging to a given `Project`."""
        return await GroupService.get_groups(session, project_id, self.default_options)

    @get("/{project_id:uuid}/{group_id:uuid}", return_dto=GroupDetailDTO)
    async def get_group_handler(self, session: AsyncSession, group_id: UUID, project_id: UUID) -> Group:
        """Gets a single `Group` belonging to a given `Project`."""
        return await GroupService.get_group(session, group_id, project_id, self.default_options)

    @post("/{project_id:uuid}", return_dto=GroupDTO)
    async def create_group_handler(
        self,
        session: AsyncSession,
        encryption: EncryptionService,
        data: JsonEncoded[GroupCreateDTO],
        project_id: UUID,
    ) -> Group:
        """Creates a `Group` under a given `Project`."""
        return await GroupService.create(session, encryption, data, project_id, self.default_options)

    @put("/{project_id:uuid}/{group_id:uuid}", return_dto=GroupDTO)
    async def update_group_handler(
        self,
        session: AsyncSession,
        group_id: UUID,
        data: JsonEncoded[GroupUpdateDTO],
        project_id: UUID,
    ) -> Group:
        """Updates a `Group` under a given `Project`."""
        return await GroupService.update(session, group_id, project_id, data, self.default_options)

    @delete("/{project_id:uuid}/{group_id:uuid}")
    async def delete_group_handler(self, session: AsyncSession, group_id: UUID, project_id: UUID) -> None:
        """Deletes a `Group` under a given `Project`."""
        if await GroupService.delete(session, group_id, project_id):
            return
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)  # TODO: raise explicit exception

    @put("/{project_id:uuid}/{group_id:uuid}/members/add", return_dto=GroupDTO)
    async def add_members_handler(
        self,
        session: AsyncSession,
        encryption: EncryptionService,
        group_id: UUID,
        project_id: UUID,
        data: JsonEncoded[GroupUsersAddDTO],
    ) -> Group:
        """Adds members to a `Group` under a given `Project`, `User`s are created the do not exists yet."""
        return await GroupService.add_members(session, encryption, group_id, project_id, data, self.default_options)

    @put("/{project_id:uuid}/{group_id:uuid}/members/remove", return_dto=GroupDTO)
    async def remove_members_handler(
        self,
        session: AsyncSession,
        group_id: UUID,
        project_id: UUID,
        data: JsonEncoded[GroupUsersRemoveDTO],
    ) -> Group:
        """Removes members from a `Group` under a given `Project`."""
        return await GroupService.remove_members(session, group_id, project_id, data)
