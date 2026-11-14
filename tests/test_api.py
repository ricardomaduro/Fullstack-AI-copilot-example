import pytest
from fastapi.testclient import TestClient

from main import app, get_people_service
from models import Person
from people_service import (
    PeopleService,
    PeopleServiceProtocol,
    create_people_service,
    read_people,
)

SECOND_PERSON = list(read_people().values())[1]


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_service_returns_person_domain_model():
    service = PeopleService({SECOND_PERSON.id: SECOND_PERSON})
    person = service.get_person_by_id(SECOND_PERSON.id)

    assert person == SECOND_PERSON


def test_people_service_implements_protocol():
    service: PeopleServiceProtocol = PeopleService(
        {SECOND_PERSON.id: SECOND_PERSON}
    )

    assert service.get_name_by_id(SECOND_PERSON.id) == SECOND_PERSON.name
    assert service.get_country_by_id(SECOND_PERSON.id) == SECOND_PERSON.country


def test_api_can_override_people_service_dependency(client):
    test_service = PeopleService({7: Person(id=7, name="Test", country="Example")})
    app.dependency_overrides[get_people_service] = lambda: test_service
    try:
        response = client.get("/people/7")
    finally:
        app.dependency_overrides.pop(get_people_service)

    assert response.status_code == 200
    assert response.json() == {"id": 7, "name": "Test", "country": "Example"}


def test_api_allows_local_react_development_origin(client):
    response = client.get(
        f"/people/{SECOND_PERSON.id}",
        headers={"Origin": "http://localhost:5173"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (
            f"/people/{SECOND_PERSON.id}",
            {
                "id": SECOND_PERSON.id,
                "name": SECOND_PERSON.name,
                "country": SECOND_PERSON.country,
            },
        ),
        (
            f"/people/{SECOND_PERSON.id}/name",
            {"id": SECOND_PERSON.id, "name": SECOND_PERSON.name},
        ),
        (
            f"/people/{SECOND_PERSON.id}/country",
            {"id": SECOND_PERSON.id, "country": SECOND_PERSON.country},
        ),
    ],
)
def test_get_person_endpoints(client, path, expected):
    response = client.get(path)

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.parametrize(
    "path",
    ["/people/999", "/people/999/name", "/people/999/country"],
)
def test_get_person_endpoints_return_404_for_unknown_id(client, path):
    response = client.get(path)

    assert response.status_code == 404
    assert response.json() == {"detail": "No person found with ID 999"}


@pytest.mark.parametrize(
    "path",
    ["/people/not-an-id", "/people/not-an-id/name", "/people/not-an-id/country"],
)
def test_get_person_endpoints_return_422_for_non_integer_id(client, path):
    response = client.get(path)

    assert response.status_code == 422


def test_service_is_created_for_each_request(monkeypatch):
    created_services = []

    def create_service():
        service = create_people_service()
        created_services.append(service)
        return service

    monkeypatch.setattr("main.create_people_service", create_service)

    with TestClient(app) as test_client:
        first_response = test_client.get(f"/people/{SECOND_PERSON.id}")
        second_response = test_client.get(f"/people/{SECOND_PERSON.id}/name")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert len(created_services) == 2
    assert created_services[0] is not created_services[1]
