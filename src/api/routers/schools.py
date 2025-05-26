from fastapi import APIRouter, HTTPException
import sqlalchemy
from src import database as db
from src.api.routers.models import SchoolCreate

router = APIRouter(prefix="/schools", tags=["schools"])

@router.post("/")
async def create_school(school: SchoolCreate):
    """Create a new school."""
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO school
                    (name, city, state, country)
                    VALUES (:name, :city, :state, :country)
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
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="school already exists!"
        )