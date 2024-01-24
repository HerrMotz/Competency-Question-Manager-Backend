from typing import Iterable, Sequence
from uuid import UUID

from domain.accounts.authentication.services import EncryptionService
from domain.accounts.models import User
from domain.accounts.services import UserService
from domain.projects.models import Project
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.base import ExecutableOption

from .dtos import GroupCreateDTO, GroupUpdateDTO, GroupUsersAddDTO, GroupUsersRemoveDTO
from .models import Group


class GroupService:
    @staticmethod
    async def get_group(
        session: AsyncSession,
        id: UUID,
        project_id: UUID | None = None,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Group:
        if project_id:
            statement = select(Group).where(Group.id == id, Group.project_id == project_id)
        else:
            statement = select(Group).where(Group.id == id)

        if options:
            statement = statement.options(*options)

        group = await session.scalar(statement)
        if not group:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND)  # TODO: raise explicit exception
        return group

    @staticmethod
    async def get_groups(
        session: AsyncSession,
        project_id: UUID | None = None,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Sequence[Group]:
        if project_id:
            statement = select(Group).where(Group.project_id == project_id)
        else:
            statement = select(Group)

        if options:
            statement = statement.options(*options)
        return (await session.scalars(statement)).all()

    @staticmethod
    async def create(
        session: AsyncSession,
        encryption: EncryptionService,
        data: GroupCreateDTO,
        project_id: UUID,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Group:
        members: list[User] = []
        if data.members:
            members_ = await UserService.get_or_create_users(session, encryption, data.members)
            members.extend([*members_.existing, *members_.created])
            # TODO: send invitation mail to all members

        group = Group(name=data.name, project_id=project_id, members=members)
        session.add(group)
        await session.commit()
        await session.refresh(group)
        return await GroupService.get_group(session, group.id, project_id, options)

    @staticmethod
    async def add_members(
        session: AsyncSession,
        encryption: EncryptionService,
        id: UUID,
        project_id: UUID,
        data: GroupUsersAddDTO,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Group:
        if not data.emails:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST)  # TODO: raise explicit exception

        group = await GroupService.get_group(session, id, project_id, [selectinload(Group.members)])
        members = await UserService.get_or_create_users(session, encryption, data.emails)
        group.members.extend([*members.existing, *members.created])
        # TODO: send invitation mail to all members

        await session.commit()
        await session.refresh(group)
        return await GroupService.get_group(session, group.id, project_id, options)

    @staticmethod
    async def remove_members(
        session: AsyncSession,
        id: UUID,
        project_id: UUID,
        data: GroupUsersRemoveDTO,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Group:
        if not data.ids:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST)  # TODO: raise explicit exception

        group = await GroupService.get_group(session, id, project_id, [selectinload(Group.members)])

        ids = set(data.ids)
        ex_members = filter(lambda user: user.id in ids, group.members)
        _ = [group.members.remove(user) for user in ex_members]

        await session.commit()
        await session.refresh(group)
        return await GroupService.get_group(session, group.id, project_id, options)

    @staticmethod
    async def update(
        session: AsyncSession,
        id: UUID,
        project_id: UUID,
        data: GroupUpdateDTO,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Group:
        group = await GroupService.get_group(session, id, project_id)
        group.name = data.name if data.name else group.name

        await session.commit()
        await session.refresh(group)
        return await GroupService.get_group(session, group.id, project_id, options)

    @staticmethod
    async def delete(
        session: AsyncSession,
        id: UUID,
        project_id: UUID,
    ) -> bool:
        result = await session.execute(delete(Group).where(Group.id == id, Group.project_id == project_id))
        return True if result.rowcount > 0 else False

    @staticmethod
    async def is_member(session: AsyncSession, id: UUID, user_id: UUID) -> bool:
        """Checks wether a given `User` is a member of the given `Group`, (Internal use only)."""
        statement = select(Group).where(Group.id == id)
        statement = statement.join(User, Group.members)
        statement = statement.filter(User.id == user_id)

        return True if await session.scalar(statement) else False

    @staticmethod
    async def is_manager(session: AsyncSession, id: UUID, user_id: UUID) -> bool:
        """Checks wether a given `User` is a manager of the `Project` a given `Group` belongs to, (Internal use only)."""
        statement = (
            select(Group)
            .where(Group.id == id)
            .options(selectinload(Group.project).options(selectinload(Project.managers)))
        )
        statement = statement.join(User, Project.managers)
        statement = statement.filter(User.id == user_id)

        return True if await session.scalar(statement) else False
