import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import CountryResponse, NameResponse, PersonResponse
from people_service import (
    PeopleServiceProtocol,
    PersonNotFoundError,
    create_people_service,
)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def get_people_service() -> PeopleServiceProtocol:
    return create_people_service()


@app.get("/people/{person_id}", response_model=PersonResponse)
def get_person(
    person_id: int,
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


@app.get("/people/{person_id}/name", response_model=NameResponse)
def get_person_name(
    person_id: int,
    service: PeopleServiceProtocol = Depends(get_people_service),
) -> NameResponse:
    try:
        name = service.get_name_by_id(person_id)
    except PersonNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return NameResponse(id=person_id, name=name)


@app.get("/people/{person_id}/country", response_model=CountryResponse)
def get_person_country(
    person_id: int,
    service: PeopleServiceProtocol = Depends(get_people_service),
) -> CountryResponse:
    try:
        country = service.get_country_by_id(person_id)
    except PersonNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return CountryResponse(id=person_id, country=country)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
