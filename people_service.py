import csv
from collections.abc import Mapping
from pathlib import Path
from threading import Lock
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


class CsvPeopleService:
    _write_lock = Lock()

    def __init__(
        self,
        people: Mapping[int, Person] | None = None,
        csv_path: Path = CSV_PATH,
    ) -> None:
        self._csv_path = csv_path
        self._people = dict(people) if people is not None else read_people(csv_path)

    def get_person_by_id(self, person_id: int) -> Person:
        person = self._people.get(int(person_id))
        if person is None:
            raise PersonNotFoundError(f"No person found with ID {person_id}")
        return person

    def get_name_by_id(self, person_id: int) -> str:
        return self.get_person_by_id(person_id).name

    def get_country_by_id(self, person_id: int) -> str:
        return self.get_person_by_id(person_id).country

    def create_person(self, name: str, country: str) -> Person:
        name = name.strip()
        country = country.strip()
        if not name or not country:
            raise ValueError("Name and country must not be empty.")

        with self._write_lock:
            current_people = read_people(self._csv_path)
            person = Person(
                id=max(current_people, default=0) + 1,
                name=name,
                country=country,
            )
            file_is_empty = self._csv_path.stat().st_size == 0
            needs_separator = False
            if not file_is_empty:
                with self._csv_path.open("rb") as file:
                    file.seek(-1, 2)
                    needs_separator = file.read(1) not in (b"\n", b"\r")

            with self._csv_path.open("a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=["ID", "Name", "Country"])
                if file_is_empty:
                    writer.writeheader()
                elif needs_separator:
                    file.write("\n")
                writer.writerow(
                    {
                        "ID": person.id,
                        "Name": person.name,
                        "Country": person.country,
                    }
                )
            self._people[person.id] = person

        return person


def create_people_service() -> PeopleServiceProtocol:
    return CsvPeopleService()
