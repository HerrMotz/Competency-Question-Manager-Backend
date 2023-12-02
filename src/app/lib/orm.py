from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import InitVar, dataclass, field
from os import environ
from typing import Callable

from advanced_alchemy.extensions.litestar.plugins.init.config import SQLAlchemyAsyncConfig
from advanced_alchemy.extensions.litestar.plugins.init.config.asyncio import autocommit_before_send_handler
from advanced_alchemy.extensions.litestar.plugins.init.plugin import SQLAlchemyInitPlugin
from litestar.config.app import AppConfig
from litestar.contrib.sqlalchemy.base import UUIDBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

_engine = create_async_engine(
    environ.get("CONNECTION_STRING", ""),
)

_async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(_engine, expire_on_commit=True)


@dataclass(frozen=True)
class AsyncSqlPlugin:
    """Wraps `litestar's` `sqlalchemy` plugin."""

    dependency_key: InitVar[str] = "session"
    config: SQLAlchemyAsyncConfig = field(init=False)
    plugin: SQLAlchemyInitPlugin = field(init=False)

    def __post_init__(self, dependency_key: str) -> None:
        config = SQLAlchemyAsyncConfig(
            session_dependency_key=dependency_key,
            engine_instance=_engine,
            session_maker=_async_session_factory,
            before_send_handler=autocommit_before_send_handler,
        )
        plugin = SQLAlchemyInitPlugin(config=config)
        object.__setattr__(self, "config", config)
        object.__setattr__(self, "plugin", plugin)

    @property
    def on_app_init(self) -> Callable[[AppConfig], AppConfig]:
        """Forwards `litestar's` plugins `on_app_init`."""
        return self.plugin.on_app_init

    async def on_startup(self) -> None:
        """Initializes the database."""
        async with self.config.get_engine().begin() as conn:
            # await conn.run_sync(UUIDBase.metadata.drop_all)
            await conn.run_sync(UUIDBase.metadata.create_all)


@asynccontextmanager
async def session() -> AsyncIterator[AsyncSession]:
    """Gets a database session using the same engine as `litestar`.

    Notes:
        * since this session is not yielded from a route handler commit,
          rollback and close need to be called explicitly

    :yield: An `AsyncSession`.
    """
    async with _async_session_factory() as session:
        yield session
