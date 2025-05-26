from fastapi import APIRouter, HTTPException
import sqlalchemy
from src import database as db
from src.api.routers.models import Department, DepartmentCreate, DepartmentLite
from typing import List, Dict, Any
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

@router.get("/")
async def list_departments(school_id: int, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """List all departments at a school."""
    with db.engine.begin() as connection:
        existing_school = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM school
                WHERE school.id = :id
                """
                ),
            {
                "id": school_id
            }
            ).first()

        if existing_school is None:
            raise HTTPException(
                status_code=404,
                detail="school does not exist!"
            )
        
        departments = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, name, abbrev
                FROM department
                WHERE department.school_id = :school_id
                LIMIT :limit
                OFFSET :offset
                """
            ),
            {
                "school_id": school_id,
                "limit": limit,
                "offset": offset
            }
        ).all()

        total_result = connection.execute(
            sqlalchemy.text(
                "SELECT COUNT(*) FROM department WHERE school_id = :school_id"
            ),
            {"school_id": school_id}
        ).scalar_one()

        departments_list = []

        for row in departments:
            Id = row.id
            Name = row.name
            Abbreviation = row.abbrev
            departments_list.append(DepartmentLite(department_id = Id, name = Name, abbrev=Abbreviation))


        return {
            "total": total_result,
            "departments": departments_list
        }
