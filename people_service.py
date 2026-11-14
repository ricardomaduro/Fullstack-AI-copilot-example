import csv
from collections.abc import Mapping
from pathlib import Path
from typing import Protocol

from models import Person

CSV_PATH = Path(__file__).with_name("data.csv")


class PersonNotFoundError(LookupError):
    """Raised when a person ID does not exist in the data source."""


class PeopleServiceProtocol(Protocol):
    def get_person_by_id(self, person_id: int) -> Person: ...

    def get_name_by_id(self, person_id: int) -> str: ...

    def get_country_by_id(self, person_id: int) -> str: ...


def read_people(csv_path: Path = CSV_PATH) -> dict[int, Person]:
    with csv_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return {
            int(row["ID"]): Person(
                id=int(row["ID"]),
                name=row["Name"],
                country=row["Country"],
            )
            for row in reader
        }


class PeopleService:
    def __init__(self, people: Mapping[int, Person] | None = None) -> None:
        self._people = dict(people) if people is not None else read_people()

    def get_person_by_id(self, person_id: int) -> Person:
        person = self._people.get(int(person_id))
        if person is None:
            raise PersonNotFoundError(f"No person found with ID {person_id}")
        return person

    def get_name_by_id(self, person_id: int) -> str:
        return self.get_person_by_id(person_id).name

    def get_country_by_id(self, person_id: int) -> str:
        return self.get_person_by_id(person_id).country


_people_service = PeopleService()


def get_people_service() -> PeopleServiceProtocol:
    return _people_service
