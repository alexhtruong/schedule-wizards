from fastapi import APIRouter, HTTPException
import sqlalchemy
from src import database as db
from src.api.routers.models import SchoolCreate

router = APIRouter(prefix="/schools", tags=["schools"])

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

        result = connection.execute(
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
        school_id = result.scalar_one()
        return {"id": str(school_id), "message": "School created successfully"}

