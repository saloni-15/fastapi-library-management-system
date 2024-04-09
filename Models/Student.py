from typing import Optional
from Models.Address import Address
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from pydantic import BaseModel, ConfigDict, Field

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]
class StudentModel(BaseModel):
    """
    Container for a single student record.
    """

    # The primary key for the StudentModel, stored as a `str` on the instance.
    # This will be aliased to `_id` when sent to MongoDB,
    # but provided as `id` in the API requests and responses.
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    age: int = Field(...)
    address: Address = Field(...)
   
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Saloni",
                "age": 22,
                "address": {"city": "Bangalore", "country": "India"}
            }
        },
    )