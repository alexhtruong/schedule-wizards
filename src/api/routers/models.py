from pydantic import BaseModel, Field, field_validator
from typing import List
import re

class Professor(BaseModel):
    id: str
    name: str = Field(min_length=2, max_length=100)
    department: str = Field(min_length=2, max_length=50)
    num_reviews: int = Field(ge=0)
    courses: List["Course"] = []

class Course(BaseModel):
    course_id: int
    name: str = Field(min_length=3, max_length=200)
    department: str = Field(min_length=2, max_length=50)
    professors: List["Professor"] = []

class Review(BaseModel):
    review_id: int
    course: Course
    term: str = Field(min_length=3, max_length=20)
    difficulty_rating: int = Field(ge=1, le=5)
    overall_rating: int = Field(ge=1, le=5)
    workload_estimate: int = Field(ge=0, le=168)
    tags: List[str] = Field(max_length=10)  # max 10 tags per review
    comments: str = Field(min_length=10, max_length=1000)

    @field_validator('term')
    def validate_term(cls, v):
        pattern = r'^(Spring|Summer|Fall|Winter)\s20\d{2}$'
        if not re.match(pattern, v):
            raise ValueError('Term must be in format "Season YYYY" (e.g. "Spring 2025")')
        return v

    @field_validator('tags')
    def validate_tags(cls, v):
        if not v:
            return v
        if not all(2 <= len(tag) <= 30 for tag in v):
            raise ValueError('Each tag must be between 2 and 30 characters')
        return v

class CourseAggregates(BaseModel):
    average_rating: float = Field(ge=0, le=5)
    average_difficulty: float = Field(ge=0, le=5)
    average_workload: float = Field(ge=0, le=168)
    total_reviews: int = Field(ge=0)
    top_tags: List[str] = Field(max_length=20)

class CourseCreate(BaseModel):
    course_code: str = Field(min_length=5, max_length=10)
    name: str = Field(min_length=3, max_length=200)
    department: str = Field(min_length=2, max_length=50)

    @field_validator('course_code')
    def validate_course_code(cls, v):
        if not re.match(r'^[A-Z]{2,4}[0-9]{3,4}[A-Z]?$', v):
            raise ValueError('Course code must be in format like "CSC101" or "ME301A"')
        return v

class Department(BaseModel):
    department_id: int
    name: str = Field(min_length=2, max_length=100)
    abbrev: str = Field(min_length=2, max_length=10)
    school_id: int = Field(ge=1)

    @field_validator('abbrev')
    def validate_abbrev(cls, v):
        if not v.isupper():
            raise ValueError('Department abbreviation must be uppercase')
        return v

class DepartmentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    abbrev: str = Field(min_length=2, max_length=10)
    school_id: int = Field(ge=1)

    @field_validator('abbrev')
    def validate_abbrev(cls, v):
        if not v.isupper():
            raise ValueError('Department abbreviation must be uppercase')
        return v

class School(BaseModel):
    id: int
    name: str = Field(min_length=2, max_length=200)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=50)
    country: str = Field(min_length=2, max_length=100)

class SchoolCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=50)
    country: str = Field(min_length=2, max_length=100)

class ProfessorDetails(BaseModel):
    professor: Professor
    reviews: List[Review]
    average_difficulty: float = Field(ge=0, le=5)
    average_workload: float = Field(ge=0, le=168)
    most_common_tags: List[str] = Field(max_length=20)

class NewProfessor(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    department: str = Field(min_length=2, max_length=50)
    metadata: dict = Field(default_factory=dict)

Professor.model_rebuild()
Course.model_rebuild()
