from httpx import Headers
from litestar import Litestar
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from litestar.testing import TestClient

from ._fixtures import admin_header, test_client  # pyright: ignore


def test_get_all(test_client: TestClient[Litestar], admin_header: Headers) -> None:
    with test_client as client:
        response = client.get(f"/projects", headers=admin_header)
        assert response.status_code == HTTP_200_OK


def test_create(test_client: TestClient[Litestar], admin_header: Headers) -> None:
    with test_client as client:
        data = {
            "name": "Mein Projekt",
            "description": "Hier könnte eine Beschreibung stehen",
            "engineers": ["jolor83823@tsderp.com"]
        }
        response = client.post(f"/projects", json=data, headers=admin_header)
        assert response.status_code == HTTP_201_CREATED


def test_get_all_w_created(test_client: TestClient[Litestar], admin_header: Headers) -> None:
    with test_client as client:
        response = client.get(f"/projects", headers=admin_header)
        assert "Mein Projekt" in [project["name"] for project in response.json()]


def test_remove(test_client: TestClient[Litestar], admin_header: Headers) -> None:
    with test_client as client:
        response = client.get(f"/projects", headers=admin_header)
        for project in filter(lambda p: p["name"] == "Mein Projekt", [project for project in response.json()]): # pyright: ignore
            response = client.delete(f"/projects/{project['id']}", headers=admin_header)
            assert response.status_code == HTTP_204_NO_CONTENT
