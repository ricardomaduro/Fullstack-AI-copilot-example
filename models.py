from dataclasses import dataclass

from pydantic import BaseModel
from pydantic import Field, field_validator


@dataclass(frozen=True)
class Person:
    id: int
    name: str
    country: str


class PersonCreateRequest(BaseModel):
    """Fields required to create a person; the API assigns the ID."""

    name: str = Field(
        min_length=1,
        max_length=100,
        description="Person's name. Leading and trailing whitespace is removed.",
        examples=["Ada Lovelace"],
    )
    country: str = Field(
        min_length=1,
        max_length=100,
        description="Person's country. Leading and trailing whitespace is removed.",
        examples=["United Kingdom"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{"name": "Ada Lovelace", "country": "United Kingdom"}]
        }
    }

    @field_validator("name", "country", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value


class PersonResponse(BaseModel):
    """A person's ID, name, and country."""

    id: int = Field(description="Unique person ID assigned by the API.")
    name: str = Field(description="Person's name.")
    country: str = Field(description="Person's country.")


class NameResponse(BaseModel):
    """A person's ID and name."""

    id: int = Field(description="Person's ID.")
    name: str = Field(description="Person's name.")


class CountryResponse(BaseModel):
    """A person's ID and country."""

    id: int = Field(description="Person's ID.")
    country: str = Field(description="Person's country.")
