from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import sqlalchemy
from src.api.routers.models import Course
from src import database as db

router = APIRouter(prefix="/reviews", tags=["reviews"])

class Professor(BaseModel):
    id: str
    name: str
    department: str
    num_reviews: int

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

class ReviewCreate(BaseModel):
    course_code: str  # e.g. "ME101", "CSC101"
    professor_name: str  # e.g. "Prof. Smith"
    term: str  # e.g. "Spring 2025"
    difficulty_rating: int = Field(ge=1, le=5)
    overall_rating: int = Field(ge=1, le=5)
    workload_estimate: int = Field(ge=0, le=168)  # max hours per week
    tags: List[str]  
    comments: str = Field(min_length=10)

    @field_validator('comments')
    def validate_comments(cls, v):
        if len(v.split()) < 5: 
            raise ValueError('Comments must be at least 5 words')
        return v

class ReportCreate(BaseModel):
    reason: str = Field(min_length=10)
    details: str = Field(min_length=20)

@router.post("/")
async def create_review(review: ReviewCreate):
    """Create a new review."""
    with db.engine.begin() as connection:
        # First get the course and professor IDs from their names/codes
        course_and_prof = connection.execute(
            sqlalchemy.text(
                """
                SELECT c.id as course_id, p.id as prof_id
                FROM course c
                JOIN professors_courses pc ON c.id = pc.course_id
                JOIN professor p ON p.id = pc.professor_id
                WHERE UPPER(c.course_code) = UPPER(:course_code) 
                AND p.name = :professor_name
                """
            ),
            {
                "course_code": review.course_code,
                "professor_name": review.professor_name
            }
        ).first()

        if not course_and_prof:
            raise HTTPException(
                status_code=400,
                detail=f"Professor {review.professor_name} is not assigned to course {review.course_code}"
            )
            
        try:
            review_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO review 
                    (course_id, term, difficulty, overall_rating, 
                    workload_rating, comments)
                    VALUES 
                    (:course_id, :term, :difficulty, :rating, 
                    :workload, :comments)
                    RETURNING id
                    """    
                ), {
                'course_id': course_and_prof.course_id,
                'term': review.term,
                'difficulty': review.difficulty_rating,
                'rating': review.overall_rating,
                'workload': review.workload_estimate,
                'comments': review.comments
            }).scalar_one()
            
            for tag in review.tags:
                # get or create tag
                tag_id = connection.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO tag 
                        (name)
                        VALUES (:name)
                        ON CONFLICT (name) DO UPDATE
                        SET name = EXCLUDED.name
                        RETURNING id
                        """    
                    ), {'name': tag}
                ).scalar()
                
                # link tag to review
                connection.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO review_tags (review_id, tag_id)
                        VALUES (:review_id, :tag_id)
                        """
                    ),
                    {'review_id': review_id, 'tag_id': tag_id}
                )

            # update course statistics
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE course c
                    SET 
                        avg_workload = COALESCE((
                            SELECT AVG(workload_rating)
                            FROM review
                            WHERE course_id = c.id
                        ), 0),
                        avg_rating = COALESCE((
                            SELECT ROUND(AVG(overall_rating), 2)
                            FROM review
                            WHERE course_id = c.id
                        ), 0)
                    WHERE c.id = :course_id
                    """
                ),
                {'course_id': course_and_prof.course_id}
            )

            # update professor statistics
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE professor p
                    SET 
                        avg_workload = COALESCE((
                            SELECT AVG(r.workload_rating)
                            FROM review r
                            JOIN professors_courses pc ON r.course_id = pc.course_id
                            WHERE pc.professor_id = p.id
                        ), 0),
                        avg_difficulty = COALESCE((
                            SELECT AVG(r.difficulty)
                            FROM review r
                            JOIN professors_courses pc ON r.course_id = pc.course_id
                            WHERE pc.professor_id = p.id
                        ), 0),
                        avg_rating = COALESCE((
                            SELECT ROUND(AVG(r.overall_rating), 2)
                            FROM review r
                            JOIN professors_courses pc ON r.course_id = pc.course_id
                            WHERE pc.professor_id = p.id
                        ), 0),
                        total_reviews = (
                            SELECT COUNT(*)
                            FROM review r
                            JOIN professors_courses pc ON r.course_id = pc.course_id
                            WHERE pc.professor_id = p.id
                        )
                    WHERE p.id = :professor_id
                    """
                ),
                {'professor_id': course_and_prof.prof_id}
            )
            return {"id": str(review_id), "message": "Review created successfully"}
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=500,
                detail="Error creating review"
            ) from e

@router.get("/course/{course_code}")
async def get_course_reviews(course_code: str):
    """Get all reviews for a specific course."""
    with db.engine.begin() as connection:
        reviews = connection.execute(
            sqlalchemy.text(
                """
                SELECT r.id, r.term, r.difficulty, r.overall_rating, 
                       r.workload_rating, r.comments,
                       c.name as course_name, c.course_code,
                       p.name as professor_name,
                       array_agg(t.name) as tags
                FROM review r
                JOIN course c ON r.course_id = c.id
                JOIN professors_courses pc ON c.id = pc.course_id
                JOIN professor p ON p.id = pc.professor_id
                LEFT JOIN review_tags rt ON r.id = rt.review_id
                LEFT JOIN tag t ON rt.tag_id = t.id
                WHERE UPPER(c.course_code) = UPPER(:course_code)
                GROUP BY r.id, r.term, r.difficulty, r.overall_rating, 
                         r.workload_rating, r.comments, c.name, 
                         c.course_code, p.name
                ORDER BY r.id DESC
                """
            ),
            {"course_code": course_code}
        ).fetchall()

        if not reviews:
            raise HTTPException(
                status_code=404,
                detail=f"No reviews found for course {course_code}"
            )

        return [
            {
                "review_id": review.id,
                "term": review.term,
                "difficulty_rating": review.difficulty,
                "overall_rating": review.overall_rating,
                "workload_estimate": review.workload_rating,
                "comments": review.comments,
                "course_name": review.course_name,
                "course_code": review.course_code,
                "professor_name": review.professor_name,
                "tags": [tag for tag in (review.tags or []) if tag is not None]
            }
            for review in reviews
        ]

@router.get("/professor/{professor_name}")
async def get_professor_reviews(professor_name: str):
    """Get all reviews for a specific professor."""
    with db.engine.begin() as connection:
        reviews = connection.execute(
            sqlalchemy.text(
                """
                SELECT r.id, r.term, r.difficulty, r.overall_rating, 
                       r.workload_rating, r.comments,
                       c.name as course_name, c.course_code,
                       p.name as professor_name,
                       array_agg(t.name) as tags
                FROM review r
                JOIN course c ON r.course_id = c.id
                JOIN professors_courses pc ON c.id = pc.course_id
                JOIN professor p ON p.id = pc.professor_id
                LEFT JOIN review_tags rt ON r.id = rt.review_id
                LEFT JOIN tag t ON rt.tag_id = t.id
                WHERE p.name = :professor_name
                GROUP BY r.id, r.term, r.difficulty, r.overall_rating, 
                         r.workload_rating, r.comments, c.name, 
                         c.course_code, p.name
                ORDER BY r.id DESC
                """
            ),
            {"professor_name": professor_name}
        ).fetchall()

        if not reviews:
            raise HTTPException(
                status_code=404,
                detail=f"No reviews found for professor {professor_name}"
            )

        return [
            {
                "review_id": review.id,
                "term": review.term,
                "difficulty_rating": review.difficulty,
                "overall_rating": review.overall_rating,
                "workload_estimate": review.workload_rating,
                "comments": review.comments,
                "course_name": review.course_name,
                "course_code": review.course_code,
                "professor_name": review.professor_name,
                "tags": [tag for tag in (review.tags or []) if tag is not None]
            }
            for review in reviews
        ]