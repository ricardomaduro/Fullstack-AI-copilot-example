from dataclasses import dataclass

from pydantic import BaseModel
from pydantic import Field, field_validator


@dataclass(frozen=True)
class Person:
    id: int
    name: str
    country: str


class PersonCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    country: str = Field(min_length=1, max_length=100)

    @field_validator("name", "country", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value


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
