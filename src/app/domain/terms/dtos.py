from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig

from .models import Term, Passage


class TermDTO(SQLAlchemyDTO[Term]):
    config = SQLAlchemyDTOConfig(
        include={"id", "project_id", "content"},
        rename_strategy="camel",
    )


class PassageDTO(SQLAlchemyDTO[Passage]):
    config = SQLAlchemyDTOConfig(
        include={"id", "author_id", "term_id", "content"},
        rename_strategy="camel",
    )
