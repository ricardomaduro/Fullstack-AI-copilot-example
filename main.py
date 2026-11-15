import uvicorn
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware

from models import (
    CountryResponse,
    NameResponse,
    PersonCreateRequest,
    PersonResponse,
)
from people_service import (
    PeopleServiceProtocol,
    PersonNotFoundError,
    create_people_service,
)


app = FastAPI(
    title="People Directory API",
    summary="Look up and create people.",
    description=(
        "A REST API for retrieving a person's name and country by ID and adding "
        "new people. New IDs are assigned automatically. The current service "
        "stores records in `data.csv`."
    ),
    version="1.0.0",
    openapi_tags=[
        {
            "name": "people",
            "description": "Create people and retrieve their details.",
        }
    ],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def get_people_service() -> PeopleServiceProtocol:
    return create_people_service()


@app.post(
    "/people",
    response_model=PersonResponse,
    status_code=201,
    summary="Create a person",
    description=(
        "Creates a person using the supplied name and country. The API assigns "
        "the next available ID and persists the record."
    ),
    response_description="The created person, including its assigned ID.",
    tags=["people"],
    responses={
        422: {
            "description": "The request body is invalid or has an empty name or country."
        }
    },
)
def create_person(
    person: PersonCreateRequest,
    service: PeopleServiceProtocol = Depends(get_people_service),
) -> PersonResponse:
    created_person = service.create_person(person.name, person.country)
    return PersonResponse(
        id=created_person.id,
        name=created_person.name,
        country=created_person.country,
    )


@app.get(
    "/people/{person_id}",
    response_model=PersonResponse,
    summary="Get a person",
    description="Returns a person's ID, name, and country.",
    response_description="The requested person.",
    tags=["people"],
    responses={404: {"description": "No person exists with the requested ID."}},
)
def get_person(
    person_id: Annotated[int, Path(ge=1, description="Positive ID of the person.")],
    service: PeopleServiceProtocol = Depends(get_people_service),
) -> PersonResponse:
    try:
        person = service.get_person_by_id(person_id)
    except PersonNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return PersonResponse(
        id=person.id,
        name=person.name,
        country=person.country,
    )


@app.get(
    "/people/{person_id}/name",
    response_model=NameResponse,
    summary="Get a person's name",
    description="Returns the name for the specified person ID.",
    response_description="The person's ID and name.",
    tags=["people"],
    responses={404: {"description": "No person exists with the requested ID."}},
)
def get_person_name(
    person_id: Annotated[int, Path(ge=1, description="Positive ID of the person.")],
    service: PeopleServiceProtocol = Depends(get_people_service),
) -> NameResponse:
    try:
        name = service.get_name_by_id(person_id)
    except PersonNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return NameResponse(id=person_id, name=name)


@app.get(
    "/people/{person_id}/country",
    response_model=CountryResponse,
    summary="Get a person's country",
    description="Returns the country for the specified person ID.",
    response_description="The person's ID and country.",
    tags=["people"],
    responses={404: {"description": "No person exists with the requested ID."}},
)
def get_person_country(
    person_id: Annotated[int, Path(ge=1, description="Positive ID of the person.")],
    service: PeopleServiceProtocol = Depends(get_people_service),
) -> CountryResponse:
    try:
        country = service.get_country_by_id(person_id)
    except PersonNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return CountryResponse(id=person_id, country=country)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
