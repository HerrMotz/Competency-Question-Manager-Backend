from typing import Annotated, Sequence, TypeVar
from uuid import UUID

from domain.accounts.authentication.services import EncryptionService
from domain.groups.models import Group
from litestar import Controller, delete, get, post, put
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_404_NOT_FOUND
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.questions.models import Question

from .dtos import GroupCreateDTO, GroupDetailDTO, GroupDTO, GroupUpdateDTO, GroupUsersAddDTO, GroupUsersRemoveDTO
from .models import Group
from .services import GroupService

T = TypeVar("T")
JsonEncoded = Annotated[T, Body(media_type=RequestEncodingType.JSON)]


class GroupController(Controller):
    path = "/groups"
    tags = ["Groups"]

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
        return await GroupService.get_groups(session, self.default_options)

    @get("/{project_id:uuid}", return_dto=GroupDetailDTO)
    async def get_group_handler(self, session: AsyncSession, project_id: UUID) -> Group:
        return await GroupService.get_group(session, project_id, self.default_options)

    @post("/", return_dto=GroupDTO)
    async def create_group_handler(
        self,
        session: AsyncSession,
        encryption: EncryptionService,
        data: JsonEncoded[GroupCreateDTO],
    ) -> Group:
        return await GroupService.create(session, encryption, data, self.default_options)

    @put("/{project_id:uuid}", return_dto=GroupDTO)
    async def update_group_handler(
        self,
        session: AsyncSession,
        project_id: UUID,
        data: JsonEncoded[GroupUpdateDTO],
    ) -> Group:
        return await GroupService.update(session, project_id, data, self.default_options)

    @delete("/{project_id:uuid}")
    async def delete_group_handler(self, session: AsyncSession, project_id: UUID) -> None:
        if await GroupService.delete(session, project_id):
            return
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)  # TODO: raise explicit exception

    @put("/{project_id:uuid}/members/add", return_dto=GroupDTO)
    async def add_members_handler(
        self,
        session: AsyncSession,
        encryption: EncryptionService,
        project_id: UUID,
        data: JsonEncoded[GroupUsersAddDTO],
    ) -> Group:
        return await GroupService.add_members(session, encryption, project_id, data, self.default_options)

    @put("/{project_id:uuid}/members/remove", return_dto=GroupDTO)
    async def remove_members_handler(
        self,
        session: AsyncSession,
        project_id: UUID,
        data: JsonEncoded[GroupUsersRemoveDTO],
    ) -> Group:
        return await GroupService.remove_members(session, project_id, data)
