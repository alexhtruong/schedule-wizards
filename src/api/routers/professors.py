from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlalchemy
from src.api.routers.models import Course, Professor
from src.api.routers.reviews import Review
from src import database as db

router = APIRouter(prefix="/professors", tags=["professors"])


class Course(BaseModel):
    course_id: int
    name: str
    department: str
    professors: List[Professor]

class Review(BaseModel):
    review_id: int
    course: Course
    term: str
    difficulty_rating: int
    overall_rating: int
    workload_estimate: int
    tags: List[str]
    comments: str
    user_id: str

class ProfessorDetails(BaseModel):
    professor: Professor
    reviews: List[Review]
    average_difficulty: float
    average_workload: float
    most_common_tags: List[str]

class NewProfessor(BaseModel):
    name: str
    department: str
    metadata: dict = {}

@router.get("/{professor_id}")
async def get_professor_details(professor_id: str) -> ProfessorDetails:
    """Get detailed information about a professor including their reviews."""
    with db.engine.begin() as connection:
        prof_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 
                    p.id,
                    p.name,
                    d.abbrev as department,
                    p.total_reviews,
                    p.avg_difficulty,
                    p.avg_workload
                FROM professor p
                JOIN department d ON p.department_id = d.id
                WHERE p.id = :prof_id
                """
            ), {"prof_id": professor_id}
        ).first()
        if not prof_result:
            raise HTTPException(status_code=404, detail="Professor not found")

        reviews_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT
                    r.id as review_id,
                    c.id as course_id,
                    c.course_code,
                    c.name as course_name,
                    r.term,
                    r.difficulty,
                    r.overall_rating,
                    r.workload_rating,
                    r.comments,
                    r.student_id
                FROM review r
                JOIN course c ON r.course_id = c.id
                JOIN professors_courses pc ON c.id = pc.course_id
                WHERE pc.professor_id = :prof_id
                """    
            ), {"prof_id": professor_id}
        )

        if not reviews_result:
            raise HTTPException(
                status_code=400,
                detail="Professor currently doesn't have reviews"
            )
        
        tags_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT t.name AS tag_name
                FROM professor_tags pt
                JOIN tag t ON pt.tag_id = t.id
                WHERE pt.professor_id = :prof_id
                GROUP BY t.name
                ORDER BY count(*) DESC
                LIMIT 10
                """    
            ), {"prof_id": professor_id})

        professor = Professor(
            id=str(prof_result.id),
            name=prof_result.name,
            department=prof_result.department,
            num_reviews=prof_result.total_reviews or 0
        )

        reviews = []
        for row in reviews_result:
            course = Course(
                id=str(row.course_id),
                code=row.course_code,
                name=row.course_name
            )
            review = Review(
                review_id=str(row.review_id),
                course=course,
                term=row.term,
                difficulty_rating=row.difficulty,
                overall_rating=row.overall_rating,
                workload_estimate=row.workload_rating,
                tags=[],
                comments=row.comments,
                user_id=str(row.student_id)
            )
            reviews.append(review)

        tags = [row.tag_name for row in tags_result]

        return ProfessorDetails(
            professor=professor,
            reviews=reviews,
            average_difficulty=float(prof_result.avg_difficulty or 0),
            average_workload=float(prof_result.avg_workload or 0),
            most_common_tags=tags
        )

@router.post("/")
async def create_professor(professor: NewProfessor):
    """Create a new professor."""
    # first check if department exists    
    with db.engine.begin() as connection:
        dept_id = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM department WHERE abbrev = :dept
                """    
            ), {'dept': professor.department}).scalar()
        if not dept_id:
            raise HTTPException(status_code=400, detail="Invalid department")
            
        new_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO professor (name, department_id) 
                VALUES (:name, :dept_id) 
                RETURNING id
                """
            ),
            {
                'name': professor.name,
                'dept_id': dept_id
            }
        ).scalar()
        
        return {"id": str(new_id), "message": "Professor created successfully"}
