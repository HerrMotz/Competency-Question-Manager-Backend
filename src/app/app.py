import os

from domain.comments.controller import CommentController
from domain.accounts.authentication.middleware import AuthenticationMiddleware
from domain.accounts.controllers import UserController
from domain.questions.controller import QuestionController
from domain.ratings.controller import RatingController
from lib.orm import AsyncSqlPlugin
from lib.services import MockDataService
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig

cors_config = CORSConfig(allow_origins=[os.environ["CORS_ALLOW_ORIGIN"]])
openapi_config = OpenAPIConfig("CQ Manager", "0.0.1", use_handler_docstrings=True)

authenticator = AuthenticationMiddleware("Super Secret Token", "Authorization", 24)
sql_plugin = AsyncSqlPlugin()

mock_data = MockDataService()

app = Litestar(
    route_handlers=[QuestionController, UserController, RatingController, CommentController],
    cors_config=cors_config,
    openapi_config=openapi_config,
    plugins=[sql_plugin.plugin],
    on_app_init=[sql_plugin.on_app_init, authenticator.on_app_init],
    on_startup=[sql_plugin.on_startup, mock_data.on_startup],
    dependencies={"authenticator": authenticator.dependency},
)
