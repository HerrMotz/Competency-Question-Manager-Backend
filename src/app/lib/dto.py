from typing import Annotated

from pydantic import BaseModel as _BaseModel
from pydantic import Field
from pydantic.functional_validators import AfterValidator


def _non_empty_string(s: str) -> str:
    assert s.strip(), f"{s} is an empty whitespace sting!"
    return s


NonEmptyString = Annotated[str, AfterValidator(_non_empty_string)]
NonEmptyStringField = Field(description="A non empty string.")


class BaseModel(_BaseModel):
    model_config = {"from_attributes": True}
