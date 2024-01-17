import sys

import pytest
from litestar import Litestar
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)
from litestar.testing import TestClient

sys.path.append("src/app/")



from app import app

def test_test() -> None:
    assert True

