from pydantic import BaseModel

class SearchStudentResponse(BaseModel):
    data : list
    
class SearchStudent(BaseModel):
    name: str
    age: int


