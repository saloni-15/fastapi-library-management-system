from pydantic import BaseModel, Field


class Address(BaseModel):
    city: str = Field(...)
    country: str = Field(...)