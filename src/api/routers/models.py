from ssl import CHANNEL_BINDING_TYPES
from unittest.util import strclass
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlalchemy


class Professor(BaseModel):
    id: str
    name: str
    department: str
    num_reviews: int

class Course(BaseModel):
    course_id: int
    name: str
    department: str
    professors: List[Professor]
