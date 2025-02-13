from typing import Annotated, Any, Sequence, TypeVar
from uuid import UUID
from lib.mails import MailService
from domain.accounts.authentication.services import EncryptionService
from domain.accounts.models import User
from domain.groups.models import Group
from domain.projects.middleware import UserProjectPermissionsMiddleware
from domain.questions.models import Question
from litestar import Controller, delete, get, post, put
from litestar.connection.request import Request
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_404_NOT_FOUND
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from litestar.background_tasks import BackgroundTasks, BackgroundTask
from litestar import Response
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

    @get("/direct/{group_id:uuid}", summary="Gets a single Group by its UUID only", return_dto=GroupDetailDTO)
    async def get_direct_handler(self, session: AsyncSession, group_id: UUID) -> Group:
        """Gets a single `Group`."""
        return await GroupService.get_group(session, group_id, None, self.default_options)

    @post("/{project_id:uuid}", return_dto=GroupDTO)
    async def create_group_handler(
        self,
        session: AsyncSession,
        encryption: EncryptionService,
        data: JsonEncoded[GroupCreateDTO],
        project_id: UUID,
        mail_service: MailService,
    ) -> Response[Group]:
        """Creates a `Group` under a given `Project`."""
        tasks: list[BackgroundTask] = []
        group, invite_task, message_task = await GroupService.create(
            session,
            encryption,
            data,
            project_id,
            self.default_options,
        )
        if invite_task:
            tasks.append(BackgroundTask(invite_task, mail_service))
        if message_task:
            tasks.append(BackgroundTask(message_task, mail_service))
        session.expunge_all()
        return Response(group, background=BackgroundTasks(tasks) if tasks else None)

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
        mail_service: MailService,
    ) -> Response[Group]:
        """Adds members to a `Group` under a given `Project`, `User`s are created the do not exists yet."""
        tasks: list[BackgroundTask] = []
        group, invite_task, message_task = await GroupService.add_members(
            session,
            encryption,
            group_id,
            project_id,
            data,
            self.default_options,
        )
        if invite_task:
            tasks.append(BackgroundTask(invite_task, mail_service))
        if message_task:
            tasks.append(BackgroundTask(message_task, mail_service))
        session.expunge_all()
        return Response(group, background=BackgroundTasks(tasks) if tasks else None)

    @put("/{project_id:uuid}/{group_id:uuid}/members/remove", return_dto=GroupDTO)
    async def remove_members_handler(
        self,
        session: AsyncSession,
        group_id: UUID,
        project_id: UUID,
        data: JsonEncoded[GroupUsersRemoveDTO],
    ) -> Group:
        """Removes members from a `Group` under a given `Project`."""
        return await GroupService.remove_members(session, group_id, project_id, data, self.default_options)

    @get("/my_groups", summary="Gets all Groups you are a member of", return_dto=GroupDTO)
    async def my_groups(self, request: Request[User, Any, Any], session: AsyncSession) -> Sequence[Group]:
        """Gets all `Group`s you are a member of."""
        return await GroupService.my_groups(session, request.user.id, options=self.default_options)

    @get("/my_groups/{project_id:uuid}", summary="Gets all Groups you are a member of", return_dto=GroupDTO)
    async def my_groups_by_projects(
        self,
        request: Request[User, Any, Any],
        session: AsyncSession,
        project_id: UUID,
    ) -> Sequence[Group]:
        """Gets all `Group`s you are a member of, filtered by a `Project`."""
        return await GroupService.my_groups(session, request.user.id, project_id, self.default_options)

    @post("/{group_id:uuid}/extend_members", return_dto=GroupDTO)
    async def extend_members_handler(
        self,
        session: AsyncSession,
        encryption: EncryptionService,
        group_id: UUID,
        data: JsonEncoded[GroupUsersAddDTO],
        mail_service: MailService,
    ) -> Response[Group]:
        """Extends the list of members in a `Group`."""
        tasks: list[BackgroundTask] = []
        group, invite_task, message_task = await GroupService.add_members(
            session,
            encryption,
            group_id,
            None,
            data,
            self.default_options,
        )
        if invite_task:
            tasks.append(BackgroundTask(invite_task, mail_service))
        if message_task:
            tasks.append(BackgroundTask(message_task, mail_service))
        session.expunge_all()
        return Response(group, background=BackgroundTasks(tasks) if tasks else None)
