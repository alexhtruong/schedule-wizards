from pydantic import BaseModel
from typing import List


class Professor(BaseModel):
    id: str
    name: str
    department: str
    num_reviews: int
    courses: List["Course"] = []

class Course(BaseModel):
    course_id: int
    name: str
    department: str
    #professors: List["Professor"] = []  

Professor.model_rebuild()
Course.model_rebuild()
