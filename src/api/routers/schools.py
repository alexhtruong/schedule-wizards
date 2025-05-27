from fastapi import APIRouter, HTTPException
import sqlalchemy
from src import database as db
from src.api.routers.models import SchoolCreate, School, DepartmentCreate, Department
from typing import Any, Dict
router = APIRouter(prefix="/schools", tags=["schools"])

# @router.post("/")
# async def create_school(school: SchoolCreate):
#     """Create a new school."""
#     try:
#         with db.engine.begin() as connection:
#             result = connection.execute(
#                 sqlalchemy.text(
#                     """
#                     INSERT INTO school
#                     (name, city, state, country)
#                     VALUES (:name, :city, :state, :country)
#                 RETURNING id
#                     """
#                 ),
#                 {
#                     "name": school.name,
#                     "city": school.city,
#                     "state": school.state,
#                     "country": school.country
#                 }
#             )
#             school_id = result.scalar_one()
#             return {"id": str(school_id), "message": "School created successfully"}
#     except sqlalchemy.exc.IntegrityError:
#         raise HTTPException(
#             status_code=409,
#             detail="school already exists!"
#         )

# @router.get("/")
# async def list_schools(limit: int = 10, offset: int = 0) -> Dict[str, Any]:
#     """List available schools."""
#     with db.engine.begin() as connection:
        
#         total_result = connection.execute(
#             sqlalchemy.text(
#                 "SELECT COUNT(*) FROM school"
#             )
#         ).scalar_one()


#         schools = connection.execute(
#             sqlalchemy.text(
#                 """
#                 SELECT id, name, city, state, country
#                 FROM school
#                 LIMIT :limit
#                 OFFSET :offset
#                 """
#             ),
#             {
#                 "limit": limit,
#                 "offset": offset
#             }
#         ).all()


#         schools_list = []

#         for row in schools:
#             Id = row.id
#             name = row.name
#             city = row.city
#             state = row.state
#             country = row.country
#             schools_list.append(School(id = Id, name =name, city=city, state = state, country = country))


#         return {
#             "total": total_result,
#             "schools": schools_list
#         }

@router.post("/departments")
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

@router.get("/departments")
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
            departments_list.append(Department(department_id = Id, name = Name, abbrev=Abbreviation))

        return {
            "total": total_result,
            "departments": departments_list
        }