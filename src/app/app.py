import os
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig

from domain.questions.controller import QuestionController
from domain.accounts.controllers import UserController
from domain.accounts.authentication.middleware import AuthenticationMiddleware

cors_config = CORSConfig(allow_origins=[os.environ["CORS_ALLOW_ORIGIN"]])
openapi_config = OpenAPIConfig("CQ Manager", "0.0.1", use_handler_docstrings=True)

authenticator = AuthenticationMiddleware("Super Secret Token", "Authorization", 24)

app = Litestar(
    route_handlers=[QuestionController, UserController],
    cors_config=cors_config,
    openapi_config=openapi_config,
    on_app_init=[authenticator.on_app_init],
    dependencies={"authenticator": authenticator.dependency},
)
