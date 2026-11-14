from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class Person:
    id: int
    name: str
    country: str


class PersonResponse(BaseModel):
    id: int
    name: str
    country: str


class NameResponse(BaseModel):
    id: int
    name: str


class CountryResponse(BaseModel):
    id: int
    country: str
