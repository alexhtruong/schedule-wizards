from fastapi import APIRouter, HTTPException
import sqlalchemy
from src import database as db
from src.api.routers.models import DepartmentCreate, Department, DepartmentStatistics
from typing import Any, Dict
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
async def list_departments(limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """List all departments at a school."""
    with db.engine.begin() as connection:
        
        departments = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, name, abbrev
                FROM department
                LIMIT :limit
                OFFSET :offset
                """
            ),
            {
                "limit": limit,
                "offset": offset
            }
        ).all()

        total_result = connection.execute(
            sqlalchemy.text(
                "SELECT COUNT(*) FROM department"
            )
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

@router.get("/{department_abbrev}/statistics", response_model=DepartmentStatistics)
async def get_department_statistics(department_abbrev: str):
    """
    Get comprehensive statistics for a department including course and professor counts,
    average ratings, and commonly used tags in reviews.
    """
    with db.engine.begin() as connection:
        # first get department info and basic stats
        dept_result = connection.execute(
            sqlalchemy.text(
                """
                WITH DeptStats AS (
                    SELECT 
                        d.id,
                        d.name,
                        d.abbrev,
                        d.school_id,
                        COUNT(DISTINCT c.id) as total_courses,
                        COUNT(DISTINCT p.id) as total_professors,
                        COUNT(DISTINCT r.id) as total_reviews,
                        ROUND(AVG(r.difficulty)::numeric, 1) as avg_difficulty,
                        ROUND(AVG(r.workload_rating)::numeric, 1) as avg_workload,
                        ROUND(AVG(r.overall_rating)::numeric, 1) as avg_rating
                    FROM department d
                    LEFT JOIN department_courses dc ON d.id = dc.department_id
                    LEFT JOIN course c ON dc.course_id = c.id
                    LEFT JOIN professors_courses pc ON c.id = pc.course_id
                    LEFT JOIN professor p ON pc.professor_id = p.id
                    LEFT JOIN review r ON r.course_id = c.id
                    WHERE d.abbrev = :dept_abbrev
                    GROUP BY d.id, d.name, d.abbrev, d.school_id
                )
                SELECT 
                    ds.*,
                    array_agg(DISTINCT t.name) FILTER (WHERE t.name IS NOT NULL) as common_tags
                FROM DeptStats ds
                LEFT JOIN department_courses dc ON ds.id = dc.department_id
                LEFT JOIN course c ON dc.course_id = c.id
                LEFT JOIN review r ON r.course_id = c.id
                LEFT JOIN review_tags rt ON r.id = rt.review_id
                LEFT JOIN tag t ON rt.tag_id = t.id
                GROUP BY ds.id, ds.name, ds.abbrev, ds.school_id, ds.total_courses, 
                         ds.total_professors, ds.total_reviews, ds.avg_difficulty, 
                         ds.avg_workload, ds.avg_rating
                """
            ),
            {"dept_abbrev": department_abbrev.upper()}
        ).first()

        if not dept_result:
            raise HTTPException(
                status_code=404,
                detail=f"Department with abbreviation '{department_abbrev}' not found"
            )

        # get most common tags
        tags_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT t.name, COUNT(*) as tag_count
                FROM department d
                JOIN department_courses dc ON d.id = dc.department_id
                JOIN course c ON dc.course_id = c.id
                JOIN review r ON r.course_id = c.id
                JOIN review_tags rt ON r.id = rt.review_id
                JOIN tag t ON rt.tag_id = t.id
                WHERE d.abbrev = :dept_abbrev
                GROUP BY t.name
                ORDER BY tag_count DESC
                LIMIT 10
                """
            ),
            {"dept_abbrev": department_abbrev.upper()}
        ).all()

        department = Department(
            department_id=dept_result.id,
            name=dept_result.name,
            abbrev=dept_result.abbrev,
            school_id=dept_result.school_id
        )

        return DepartmentStatistics(
            department=department,
            total_courses=dept_result.total_courses or 0,
            total_professors=dept_result.total_professors or 0,
            average_difficulty=float(dept_result.avg_difficulty or 0),
            average_workload=float(dept_result.avg_workload or 0),
            average_rating=float(dept_result.avg_rating or 0),
            total_reviews=dept_result.total_reviews or 0,
            most_common_tags=[tag.name for tag in tags_result]
        )
