import os

from lib.orm import AsyncSqlPlugin

sql_plugin = AsyncSqlPlugin()


from domain.accounts.authentication.middleware import AuthenticationMiddleware
from domain.accounts.authentication.services import EncryptionService
from domain.accounts.controllers import UserController
from domain.consolidations.controllers import ConsolidationController
from domain.groups.controllers import GroupController
from domain.projects.controllers import ProjectController
from domain.questions.controller import QuestionController
from domain.rating.controller import RatingController
from domain.terms.controllers import TermController
from lib.services import MockDataService
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig

cors_config = CORSConfig(allow_origins=[os.environ["CORS_ALLOW_ORIGIN"]])
openapi_config = OpenAPIConfig("CQ Manager", "0.0.1", use_handler_docstrings=True)

authenticator = AuthenticationMiddleware("Super Secret Token", "Authorization", 24)
encryption = EncryptionService()

mock_data = MockDataService()

app = Litestar(
    route_handlers=[
        QuestionController,
        UserController,
        RatingController,
        ProjectController,
        GroupController,
        ConsolidationController,
        TermController,
    ],
    cors_config=cors_config,
    openapi_config=openapi_config,
    plugins=[sql_plugin.plugin],
    on_app_init=[sql_plugin.on_app_init, authenticator.on_app_init],
    on_startup=[sql_plugin.on_startup, mock_data.on_startup],
    dependencies={
        "authenticator": authenticator.dependency,
        "encryption": encryption.dependency,
    },
)
