from typing import Any, Type, TypeVar

from litestar.connection.base import ASGIConnection

T = TypeVar("T")


def get_path_param(_: Type[T], param: str, connection: ASGIConnection[Any, Any, Any, Any]) -> T | None:
    """Walruses can't write type hints and functions lack support for generics (just pre 3.12 things)."""
    return connection.path_params.get(param, None)
