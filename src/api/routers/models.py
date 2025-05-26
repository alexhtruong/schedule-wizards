from pydantic import BaseModel, Field, field_validator
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
    professors: List["Professor"] = []  

class Review(BaseModel):
    review_id: int
    course: Course
    term: str
    difficulty_rating: int
    overall_rating: int
    workload_estimate: int
    tags: List[str]
    comments: str

    
class CourseAggregates(BaseModel):
    average_rating: float
    average_difficulty: float
    average_workload: float
    total_reviews: int
    top_tags: List[str]

class CourseCreate(BaseModel):
    course_code: str
    name: str
    department: str

class Department(BaseModel):
    department_id: int
    name: str
    abbrev: str
    school_id: int

class DepartmentCreate(BaseModel):
    name: str
    abbrev: str
    school_id: int

class DepartmentLite(BaseModel):
    department_id: int
    name: str
    abbrev: str

class ReviewCreate(BaseModel):
    course_code: str  # e.g. "ME101", "CSC101"
    professor_name: str  # e.g. "Prof. Smith"
    term: str  # e.g. "Spring 2025"
    difficulty_rating: int = Field(ge=1, le=5)
    overall_rating: int = Field(ge=1, le=5)
    workload_estimate: int = Field(ge=0, le=168)  # max hours per week
    tags: List[str]  
    comments: str = Field(min_length=10)

    @field_validator('comments')
    def validate_comments(cls, v):
        if len(v.split()) < 5: 
            raise ValueError('Comments must be at least 5 words')
        return v

class School(BaseModel):
    id: int
    name: str
    city: str
    state: str
    country: str

class SchoolCreate(BaseModel):
    name: str
    city: str
    state: str
    country: str

class ProfessorDetails(BaseModel):
    professor: Professor
    reviews: List[Review]
    average_difficulty: float
    average_workload: float
    most_common_tags: List[str]

class NewProfessor(BaseModel):
    name: str
    department: str
    metadata: dict = {}

Professor.model_rebuild()
Course.model_rebuild()
