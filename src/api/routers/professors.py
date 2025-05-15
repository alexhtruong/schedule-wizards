from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlalchemy
from src.api.routers.models import Course, Professor
from src.api.routers.reviews import Review
from src import database as db

router = APIRouter(prefix="/professors", tags=["professors"])

class Review(BaseModel):
    review_id: int
    course: Course
    term: str
    difficulty_rating: int
    overall_rating: int
    workload_estimate: int
    tags: List[str]
    comments: str

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

# TODO: allow metadata to be attaching courses to professor
# TODO: add endpoint for attaching courses to a professor
@router.get("/{professor_id}")
async def get_professor_details(professor_id: str) -> ProfessorDetails:
    """Get detailed information about a professor including their reviews and courses."""
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

        # fetch all courses for this professor
        courses_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 
                    c.id,
                    c.course_code,
                    c.name,
                    d.abbrev as department
                FROM course c
                JOIN professors_courses pc ON c.id = pc.course_id
                JOIN department d ON c.department_id = d.id
                WHERE pc.professor_id = :prof_id
                """
            ), {"prof_id": professor_id}
        ).all()

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
                    r.comments
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

        courses = [
            {
                "course_id": int(row.id),  
                "name": row.name,
                "department": row.department,
                "professors": []
            } for row in courses_result
        ]
        print(courses)

        professor = Professor(
            id=str(prof_result.id),
            name=prof_result.name,
            department=prof_result.department,
            num_reviews=prof_result.total_reviews or 0,
            courses=courses
        )

        reviews = []
        for row in reviews_result:
            course = {
                "course_id": int(row.course_id),
                "name": row.course_name,
                "department": "",  
                "professors": []  
            }
            review = Review(
                review_id=str(row.review_id),
                course=course,
                term=row.term,
                difficulty_rating=row.difficulty,
                overall_rating=row.overall_rating,
                workload_estimate=row.workload_rating,
                tags=[],
                comments=row.comments,
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

@router.post("/{professor_id}/courses")
async def attach_courses_to_professor(
    professor_id: str,
    course_codes: List[str]
) -> dict:
    """Attach courses to a professor."""
    with db.engine.begin() as connection:
        # first verify the professor exists
        professor = connection.execute(
            sqlalchemy.text(
                "SELECT id FROM professor WHERE id = :prof_id"
            ),
            {"prof_id": professor_id}
        ).first()
        
        if not professor:
            raise HTTPException(
                status_code=404,
                detail="Professor not found"
            )
        
        # verify all courses exist and get their IDs
        courses = connection.execute(
            sqlalchemy.text(
                "SELECT id, course_code FROM course WHERE course_code = ANY(:course_codes)"
            ),
            {"course_codes": course_codes}
        ).all()
        
        if len(courses) != len(course_codes):
            raise HTTPException(
                status_code=400,
                detail="One or more course codes are invalid"
            )
            
        # add the associations
        for course in courses:
            try:
                connection.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO professors_courses (professor_id, course_id)
                        VALUES (:prof_id, :course_id)
                        ON CONFLICT DO NOTHING
                        """
                    ),
                    {
                        "prof_id": professor_id,
                        "course_id": course.id
                    }
                )
            except sqlalchemy.exc.IntegrityError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid association between professor {professor_id} and course {course.course_code}"
                )
                
        return {"message": f"Successfully attached {len(course_codes)} courses to professor {professor_id}"}
