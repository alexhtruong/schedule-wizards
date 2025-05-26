from fastapi import APIRouter, HTTPException
import sqlalchemy
from src import database as db
from src.api.routers.models import SchoolCreate, School
from typing import List, Any, Dict
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

    

@router.get("/")
async def list_schools(limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """List available schools."""
    with db.engine.begin() as connection:
        
        total_result = connection.execute(
            sqlalchemy.text(
                "SELECT COUNT(*) FROM school"
            )
        ).scalar_one()


        schools = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, name, city, state, country
                FROM school
                LIMIT :limit
                OFFSET :offset
                """
            ),
            {
                "limit": limit,
                "offset": offset
            }
        ).all()


        schools_list = []

        for row in schools:
            Id = row.id
            name = row.name
            city = row.city
            state = row.state
            country = row.country
            schools_list.append(School(id = Id, name =name, city=city, state = state, country = country))


        return {
            "total": total_result,
            "schools": schools_list
        }


        
