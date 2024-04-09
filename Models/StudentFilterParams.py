from typing import Optional
from pydantic import BaseModel, Field

class StudentFilterParams(BaseModel):
    country: Optional[str] = Field(description="query country")
    age: Optional[int] = Field(description="query age")
    