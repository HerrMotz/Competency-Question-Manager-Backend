import sys

import pytest
from httpx import Headers
from litestar import Litestar
from litestar.status_codes import HTTP_201_CREATED
from litestar.testing import TestClient

sys.path.append("src/app/")


from app import app


def get_admin_header(test_client: TestClient[Litestar]) -> Headers:
    with test_client as client:
        data = {
            "email": "admin@uni-jena.de",
            "password": "HalloWelt123",
        }
        response = client.post(f"/users/login", json=data)
        assert response.status_code == HTTP_201_CREATED
        assert response.headers.get("Authorization", None) is not None
        return response.headers


@pytest.fixture(scope="module")
def admin_header() -> Headers:
    return get_admin_header(TestClient(app=app))  # type: ignore


@pytest.fixture(scope="module")
def test_client() -> TestClient[Litestar]:
    return TestClient(app=app)  # type: ignore
