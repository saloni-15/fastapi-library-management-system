import os
from typing import Optional, List

from Models.SearchStudentResponse import SearchStudent, SearchStudentResponse
from fastapi import Depends, FastAPI, Body, HTTPException, status
from fastapi.responses import Response
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from Models.StudentFilterParams import StudentFilterParams

from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument

from Models import Student, StudentId

app = FastAPI(
    title="Student Course API",
    summary="A sample application showing how to use FastAPI to add a ReST API to a MongoDB collection.",
)
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.get_database("libraryDB")
student_collection = db.get_collection("students")



    
class UpdateStudentModel(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    name: Optional[str] = None
    email: Optional[EmailStr] = None
    course: Optional[str] = None
    gpa: Optional[float] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": 3.0,
            }
        },
    )


class StudentCollection(BaseModel):
    """
    A container holding a list of `StudentModel` instances.

    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """

    students: List[Student.StudentModel]

# Create new student
@app.post(
    "/students/",
    response_description="A JSON response sending back the ID of the newly created student record.",
    response_model=StudentId.StudentId,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_student(student: Student.StudentModel = Body(...)):
    print("creating student...")
    """
    Insert a new student record.

    A unique `id` will be created and provided in the response.
    """
    new_student = await student_collection.insert_one(
        student.model_dump(by_alias=True, exclude=["id"])
    )
    created_student = await student_collection.find_one(
        {"_id": new_student.inserted_id}
    )
    print("created student: ", new_student.inserted_id)
    response = StudentId.StudentId(id = str(new_student.inserted_id))
    return response



#Get all students
@app.get(
    "/students/",
    response_description="List filtered students",
    response_model=SearchStudentResponse,
    response_model_by_alias=False,
)
async def list_filtered_students(query_params: StudentFilterParams = Depends()):
    """
    List student data based on given filters in the database.

    The response is unpaginated and limited to 1000 results.
    """
    students = None
    if (query_params.country != None and query_params.age != None):
        students = await student_collection.find({"address.country": query_params.country, "age": {"$gte": query_params.age}}).to_list(1000)
        #students =  await student_collection.find(f'{{"address.country": {query_params.country}, "age": {{"$gte": {query_params.age}}}}}')
    elif (query_params.country != None):
        students =  await student_collection.find({"address.country": query_params.country})
    elif (query_params.age != None):
        students =  await student_collection.find({"age": {"$gte": query_params.age}})
    else:
        students = await student_collection.find().to_list(1000)
    response = []
    for student in students:
        print("printtt" , student)
        res = SearchStudent(name = student["name"], age = student["age"])
        response.append(res)   

    print(students)
    return SearchStudentResponse(data = response)


@app.get(
    "/students/{id}",
    response_description="Get a single student",
    response_model=Student.StudentModel,
    response_model_by_alias=False,
)
async def show_student(id: str):
    """
    Get the record for a specific student, looked up by `id`.
    """
    if (
        student := await student_collection.find_one({"_id": ObjectId(id)})
    ) is not None:
        return student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


@app.put(
    "/students/{id}",
    response_description="Update a student",
    response_model=Student.StudentModel,
    response_model_by_alias=False,
)
async def update_student(id: str, student: UpdateStudentModel = Body(...)):
    """
    Update individual fields of an existing student record.

    Only the provided fields will be updated.
    Any missing or `null` fields will be ignored.
    """
    student = {
        k: v for k, v in student.model_dump(by_alias=True).items() if v is not None
    }

    if len(student) >= 1:
        update_result = await student_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": student},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Student {id} not found")

    # The update is empty, but we should still return the matching document:
    if (existing_student := await student_collection.find_one({"_id": id})) is not None:
        return existing_student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


@app.delete("/students/{id}", response_description="Delete a student")
async def delete_student(id: str):
    """
    Remove a single student record from the database.
    """
    delete_result = await student_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Student {id} not found")
