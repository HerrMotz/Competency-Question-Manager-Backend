from typing import Iterable, Sequence
from uuid import UUID

from domain.accounts.authentication.services import EncryptionService
from domain.accounts.models import User
from domain.accounts.services import UserService
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.base import ExecutableOption

from .dtos import ProjectCreateDTO, ProjectUpdateDTO, ProjectUsersAddDTO, ProjectUsersRemoveDTO
from .models import Project


class ProjectService:
    @staticmethod
    async def get_project(
        session: AsyncSession,
        id: UUID,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Project:
        statement = select(Project).where(Project.id == id)
        if options:
            statement = statement.options(*options)

        project = await session.scalar(statement)
        if not project:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND)  # TODO: raise explicit exception
        return project

    @staticmethod
    async def get_projects(
        session: AsyncSession, options: Iterable[ExecutableOption] | None = None
    ) -> Sequence[Project]:
        statement = select(Project)
        if options:
            statement = statement.options(*options)
        return (await session.scalars(statement)).all()

    @staticmethod
    async def create(
        session: AsyncSession,
        encryption: EncryptionService,
        data: ProjectCreateDTO,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Project:
        managers: list[User] = []
        if data.managers:
            managers_ = await UserService.get_or_create_users(session, encryption, data.managers)
            managers.extend([*managers_.existing, *managers_.created])
            # TODO: send invitation mail to all managers

        engineers: list[User] = []
        if data.engineers:
            engineers_ = await UserService.get_or_create_users(session, encryption, data.engineers)
            engineers.extend([*engineers_.existing, *engineers_.created])
            # TODO: send invitation mail to all engineers

        project = Project(name=data.name, description=data.description, managers=managers, engineers=engineers)
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return await ProjectService.get_project(session, project.id, options)

    @staticmethod
    async def add_managers(
        session: AsyncSession,
        encryption: EncryptionService,
        id: UUID,
        data: ProjectUsersAddDTO,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Project:
        if not data.emails:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST)  # TODO: raise explicit exception

        project = await ProjectService.get_project(session, id, [selectinload(Project.managers)])
        managers = await UserService.get_or_create_users(session, encryption, data.emails)
        project.managers.extend([*managers.existing, *managers.created])
        # TODO: send invitation mail to all managers

        await session.commit()
        await session.refresh(project)
        return await ProjectService.get_project(session, project.id, options)

    @staticmethod
    async def remove_managers(
        session: AsyncSession,
        id: UUID,
        data: ProjectUsersRemoveDTO,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Project:
        if not data.ids:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST)  # TODO: raise explicit exception

        project = await ProjectService.get_project(session, id, [selectinload(Project.managers)])

        ids = set(data.ids)
        ex_managers = filter(lambda user: user.id in ids, project.managers)
        _ = [project.managers.remove(user) for user in ex_managers]

        await session.commit()
        await session.refresh(project)
        return await ProjectService.get_project(session, project.id, options)

    @staticmethod
    async def add_engineers(
        session: AsyncSession,
        encryption: EncryptionService,
        id: UUID,
        data: ProjectUsersAddDTO,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Project:
        if not data.emails:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST)  # TODO: raise explicit exception

        engineers = await UserService.get_or_create_users(session, encryption, data.emails)
        project = await ProjectService.get_project(session, id, [selectinload(Project.engineers)])
        project.engineers.extend([*engineers.existing, *engineers.created])
        # TODO: send invitation mail to all engineers

        await session.commit()
        await session.refresh(project)
        return await ProjectService.get_project(session, project.id, options)

    @staticmethod
    async def remove_engineers(
        session: AsyncSession,
        id: UUID,
        data: ProjectUsersRemoveDTO,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Project:
        if not data.ids:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST)  # TODO: raise explicit exception

        project = await ProjectService.get_project(session, id, [selectinload(Project.engineers)])

        ids = set(data.ids)
        ex_engineers = filter(lambda user: user.id in ids, project.engineers)
        _ = [project.engineers.remove(user) for user in ex_engineers]

        await session.commit()
        await session.refresh(project)
        return await ProjectService.get_project(session, project.id, options)

    @staticmethod
    async def update(
        session: AsyncSession,
        id: UUID,
        data: ProjectUpdateDTO,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Project:
        project = await ProjectService.get_project(session, id)
        project.name = data.name if data.name else project.name
        project.description = data.description if data.description else project.description

        await session.commit()
        await session.refresh(project)
        return await ProjectService.get_project(session, project.id, options)

    @staticmethod
    async def delete(session: AsyncSession, id: UUID) -> bool:
        result = await session.execute(delete(Project).where(Project.id == id))
        return True if result.rowcount > 0 else False
