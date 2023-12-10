from typing import Iterable, Sequence
from uuid import UUID

from domain.accounts.services import UserService
from litestar.background_tasks import BackgroundTask
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.base import ExecutableOption

from .dtos import ProjectCreateDTO, ProjectManagersAddDTO, ProjectManagersRemoveDTO, ProjectUpdateDTO
from .models import Project


class ProjectService:
    @staticmethod
    async def get_project(session: AsyncSession, id: UUID, options: Iterable[ExecutableOption] | None = None) -> Project:
        statement = select(Project).where(Project.id == id)
        if options:
            statement = statement.options(*options)

        project = await session.scalar(statement)
        if not project:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND)  # TODO: raise explicit exception
        return project

    @staticmethod
    async def get_projects(session: AsyncSession, options: Iterable[ExecutableOption] | None = None) -> Sequence[Project]:
        statement = select(Project)
        if options:
            statement = statement.options(*options)
        return (await session.scalars(statement)).all()

    @staticmethod
    async def create(session: AsyncSession, data: ProjectCreateDTO) -> tuple[Project, BackgroundTask | None]:
        users, invite_task = None, None
        if data.managers:
            users, invite_task = await UserService.get_system_users(session, data.managers)

        project = Project(name=data.name, description=data.description, managers=users if users else [])
        session.add(project)
        await session.refresh(project)
        return project, invite_task

    @staticmethod
    async def add_managers(session: AsyncSession, id: UUID, data: ProjectManagersAddDTO) -> tuple[Project, BackgroundTask | None]:
        project = await ProjectService.get_project(session, id, [selectinload(Project.managers)])

        users, invite_task = None, None
        if data:
            users, invite_task = await UserService.get_system_users(session, data)

        project.managers.extend(users) if users else ...
        return project, invite_task

    @staticmethod
    async def remove_managers(session: AsyncSession, id: UUID, data: ProjectManagersRemoveDTO) -> Project:
        project = await ProjectService.get_project(session, id, [selectinload(Project.managers)])

        ids = set(data)
        ex_managers = filter(lambda user: user.id in ids, project.managers)
        _ = [project.managers.remove(user) for user in ex_managers]

        return project

    @staticmethod
    async def update(session: AsyncSession, id: UUID, data: ProjectUpdateDTO) -> Project:
        project = await ProjectService.get_project(session, id)
        project.name = data.name if data.name else project.name
        project.description = data.description if data.description else project.description
        return project

    @staticmethod
    async def delete(session: AsyncSession, id: UUID) -> bool:
        result = await session.execute(delete(Project).where(Project.id == id))
        return True if result.rowcount > 0 else False
