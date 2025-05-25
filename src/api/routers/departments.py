from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlalchemy
from src.api.routers.models import Course, Professor
from src import database as db

router = APIRouter(prefix="/departments", tags=["departments"])

class Department(BaseModel):
    department_id: int
    name: str
    abbrev: str
    school_id: int

class DepartmentCreate(BaseModel):
    name: str
    abbrev: str
    school_id: int


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
            {
                "id": department.school_id
            }
            ).first()

        if existing_school is None:
            raise HTTPException(
                status_code=400,
                detail="school does not exist!"
            )
        
        existing_department = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM department
                WHERE department.name = :name AND department.school_id = :school_id
                """
            ),
            {
                "name": department.name,
                "school_id": department.school_id
            }
        ).first()

        if existing_department is not None:
            raise HTTPException(
                status_code=400,
                detail="department already exists!"
            )

        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO department
                (name,
                abbrev,
                school_id)
                VALUES
                (:name, :abbrev, :school_id)
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
