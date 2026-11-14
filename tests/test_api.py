import pytest
from fastapi.testclient import TestClient

from main import app
from models import Person
from people_service import PeopleService, PeopleServiceProtocol, get_people_service

client = TestClient(app)


def test_service_returns_person_domain_model():
    service = PeopleService({2: Person(id=2, name="Maria", country="Portugal")})
    person = service.get_person_by_id(2)

    assert person == Person(id=2, name="Maria", country="Portugal")


def test_people_service_implements_protocol():
    service: PeopleServiceProtocol = PeopleService(
        {2: Person(id=2, name="Maria", country="Portugal")}
    )

    assert service.get_name_by_id(2) == "Maria"
    assert service.get_country_by_id(2) == "Portugal"


def test_api_can_override_people_service_dependency():
    test_service = PeopleService({7: Person(id=7, name="Test", country="Example")})
    app.dependency_overrides[get_people_service] = lambda: test_service
    try:
        response = client.get("/people/7")
    finally:
        app.dependency_overrides.pop(get_people_service)

    assert response.status_code == 200
    assert response.json() == {"id": 7, "name": "Test", "country": "Example"}


def test_api_allows_local_react_development_origin():
    response = client.get("/people/2", headers={"Origin": "http://localhost:5173"})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/people/2", {"id": 2, "name": "Maria", "country": "Portugal"}),
        ("/people/2/name", {"id": 2, "name": "Maria"}),
        ("/people/2/country", {"id": 2, "country": "Portugal"}),
    ],
)
def test_get_person_endpoints(path, expected):
    response = client.get(path)

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.parametrize(
    "path",
    ["/people/999", "/people/999/name", "/people/999/country"],
)
def test_get_person_endpoints_return_404_for_unknown_id(path):
    response = client.get(path)

    assert response.status_code == 404
    assert response.json() == {"detail": "No person found with ID 999"}


@pytest.mark.parametrize(
    "path",
    ["/people/not-an-id", "/people/not-an-id/name", "/people/not-an-id/country"],
)
def test_get_person_endpoints_return_422_for_non_integer_id(path):
    response = client.get(path)

    assert response.status_code == 422
