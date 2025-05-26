from fastapi import APIRouter, HTTPException
import sqlalchemy
from src import database as db
from src.api.routers.models import DepartmentCreate

router = APIRouter(prefix="/departments", tags=["departments"])


@router.post("/")
async def create_department(department: DepartmentCreate):
    """Create a new department."""
    with db.engine.begin() as connection:
        existing_school = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM school
                WHERE school.id = :id
                """
            ),
            {"id": department.school_id}
        ).first()

        if existing_school is None:
            raise HTTPException(
                status_code=404,
                detail="School does not exist!"
            )
        
        try:
            result = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO department
                    (name, abbrev, school_id)
                    VALUES (:name, :abbrev, :school_id)
                    RETURNING id
                    """
                ),
                {
                    "name": department.name,
                    "abbrev": department.abbrev,
                    "school_id": department.school_id
                }
            )
            department_id = result.scalar_one()
            return {"id": str(department_id), "message": "Department created successfully"}
        except sqlalchemy.exc.IntegrityError as e:
            raise HTTPException(
            status_code=409,
            detail="Department already exists"
            ) from e