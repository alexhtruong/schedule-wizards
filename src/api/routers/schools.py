from ssl import CHANNEL_BINDING_TYPES
from unittest.util import strclass
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlalchemy
from src.api.routers.courses import Course
from src.api.routers.reviews import Review
from src import database as db

router = APIRouter(prefix="/schools", tags=["schools"])

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
    

@router.post("/")
async def create_school(school: SchoolCreate):
    """Create a new school."""
    with db.engine.begin() as connection:
        existing_school = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM school
                WHERE school.name = :name AND school.state = :state
                """
            ),
            {
                "name": school.name,
                "state": school.state
            }
        ).first()

        if existing_school is not None:
            raise HTTPException(
                status_code=400,
                detail="school already exists!"
            )

        school_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO school
                (name,
                city,
                state,
                country)
                VALUES
                (:name, :city, :state, :country)
                RETURNING id
                """
            ),
            {
                "name": school.name,
                "city": school.city,
                "state": school.state,
                "country": school.country
            }
        )
        return {"id": str(school_id), "message": "School created successfully"}

