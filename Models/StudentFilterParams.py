from typing import Optional
from pydantic import BaseModel, Field

class StudentFilterParams(BaseModel):
    country: Optional[str] = Field(None, description="query country")
    age: Optional[int] = Field(None, description="query age")
    
    