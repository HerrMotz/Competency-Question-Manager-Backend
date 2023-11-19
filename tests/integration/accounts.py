import sys

import pytest
from litestar import Litestar
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from litestar.testing import TestClient

sys.path.append("src/app/")


from app import app


@pytest.fixture(scope="function")
def test_client() -> TestClient[Litestar]:
    return TestClient(app=app)  # type: ignore


user_id = None


def test_register_user(test_client: TestClient[Litestar]) -> None:
    with test_client as client:
        data = {
            "email": "dominik@uni-jena.de",
            "name": "dominik",
            "password": "12345",
        }

        response = client.post("/users/register", json=data)
        assert response.status_code == HTTP_201_CREATED

        global user_id
        user_id = response.json()["id"]


def test_verify_user(test_client: TestClient[Litestar]) -> None:
    with test_client as client:
        response = client.put(f"/users/verify/{user_id}")
        assert response.status_code == HTTP_200_OK
        assert response.json()["is_verified"] == True


def test_update_user(test_client: TestClient[Litestar]) -> None:
    with test_client as client:
        response = client.put(f"/users/{user_id}", json={"name": "dominik_neu"})
        assert response.status_code == HTTP_200_OK
        assert response.json()["name"] == "dominik_neu"


def test_get_user(test_client: TestClient[Litestar]) -> None:
    with test_client as client:
        response = client.get(f"/users/{user_id}")
        assert response.status_code == HTTP_200_OK
        assert response.json()["name"] == "dominik"


def test_get_users(test_client: TestClient[Litestar]) -> None:
    with test_client as client:
        response = client.get(f"/users")
        assert response.status_code == HTTP_200_OK


def test_delete_users(test_client: TestClient[Litestar]) -> None:
    with test_client as client:
        response = client.delete(f"/users/{user_id}")
        assert response.status_code == HTTP_204_NO_CONTENT
