
from pydantic import BaseModel, Field

class StudentFilterParams(BaseModel):
    country: str = Field(description="query country")
    age: int = Field(description="query age")
    