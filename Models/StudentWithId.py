from typing import Optional
from Models.Address import Address
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from pydantic import BaseModel, ConfigDict, Field

class StudentWithId(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    address: Optional[Address] = None
 