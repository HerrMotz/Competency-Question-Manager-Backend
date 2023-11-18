import os
from litestar import Litestar
from litestar.config.cors import CORSConfig

from domain.questions.controller import QuestionController

cors_config = CORSConfig(allow_origins=[os.environ['CORS_ALLOW_ORIGIN']])

app = Litestar(
    route_handlers=[QuestionController],
    cors_config=cors_config,
)



