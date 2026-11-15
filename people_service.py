import csv
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

    def create_person(self, name: str, country: str) -> Person: ...


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


def create_people_service() -> PeopleServiceProtocol:
    from csv_people_service import CsvPeopleService

    return CsvPeopleService()
