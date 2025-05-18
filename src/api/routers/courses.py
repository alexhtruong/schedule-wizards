from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlalchemy
from src import database as db
from src.api.routers.models import Professor, Course


router = APIRouter(prefix="/courses", tags=["courses"])


class CourseAggregates(BaseModel):
    average_rating: float
    average_difficulty: float
    average_workload: float
    total_reviews: int
    top_tags: List[str]

class CourseCreate(BaseModel):
    course_code: str
    name: str
    department: str

@router.get("/")
async def list_courses(
    department: Optional[str] = None,
    sort_by: Optional[str] = "workload",
    order: str = Query("desc", pattern="^(asc|desc)$"),
) -> List[Course]:
    """List courses with optional filters and sorting."""
    if sort_by not in ["workload", "rating"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort_by value. Use 'workload' or 'rating'."
        )
    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid order value. Use 'asc' or 'desc'."
        )
    
    query = """
    SELECT 
        d.id AS department_id,
        d.abbrev AS department,
        c.id AS course_id,
        c.name AS name,
        p.id AS prof_id,
        p.name AS prof_name,
        p.total_reviews AS num_reviews
    FROM department d
    JOIN department_courses dc ON d.id = dc.department_id
    LEFT JOIN course c ON dc.course_id = c.id
    LEFT JOIN professors_courses pc ON c.id = pc.course_id
    LEFT JOIN professor p ON pc.professor_id = p.id
    """
    params = {}
    
    # apply filters
    if department:
        query += " AND d.abbrev = :dept"
        params['dept'] = department
        
    # apply sorting
    if sort_by == 'workload':
        query += f" ORDER BY c.avg_workload {order}"
    elif sort_by == 'rating':
        query += f" ORDER BY c.avg_rating {order}"
        
    with db.engine.begin() as conn:
        result = conn.execute(
            sqlalchemy.text(query),
            params
        ).all()

    if not result:
        raise HTTPException(status_code=404, detail="No courses found")
        
    courses_dict = {}
    for row in result:
        if row.course_id not in courses_dict:
            courses_dict[row.course_id] = Course(
                course_id=row.course_id,
                name=row.name,
                department=row.department,
                professors=[]
            )
        # Only append professor if both id and name exist
        if row.prof_id is not None and row.prof_name is not None:
            courses_dict[row.course_id].professors.append(
                Professor(
                    id=str(row.prof_id),
                    name=row.prof_name,
                    department=row.department,
                    num_reviews=row.num_reviews
                )
            )
            
    return list(courses_dict.values())

@router.get("/{course_code}")
async def get_course(course_code: str) -> Course:
    """Get a specific course's details by name."""
    with db.engine.begin() as conn:
        result = conn.execute(
            sqlalchemy.text(
                """
                SELECT
                    c.id as course_id,
                    c.name,
                    d.abbrev as department,
                    p.id as prof_id,
                    p.name as prof_name,
                    p.total_reviews as total_reviews
                FROM course c
                JOIN department_courses dc ON c.id = dc.course_id
                JOIN department d ON dc.department_id = d.id
                LEFT JOIN professors_courses pc ON c.id = pc.course_id
                LEFT JOIN professor p ON pc.professor_id = p.id
                WHERE c.course_code = :course_code
                """
            ),
            {"course_code": course_code.upper()}
        ).all()

        if not result:
            raise HTTPException(status_code=404, detail="Course not found")
        
        courses_dict = {}
        for row in result:
            if row.course_id not in courses_dict:
                courses_dict[row.course_id] = Course(
                    course_id=row.course_id,
                    name=row.name,
                    department=row.department,
                    professors=[]
                )
            if row.prof_id is not None and row.prof_name is not None:
                courses_dict[row.course_id].professors.append(
                    Professor(
                        id=str(row.prof_id),
                        name=row.prof_name,
                        department=row.department,
                        num_reviews=row.total_reviews or 0
                    )
                )
 
        if len(courses_dict) != 1:
            raise HTTPException(
                status_code=500,
                detail="Expected exactly one course, found multiple"
            )
    
        return list(courses_dict.values())[0]


@router.get("/{course_code}/professors")
async def get_course_professors(course_code: str) -> List[Professor]:
    """Get professors teaching a specific course by its code (e.g., 'ME101', 'CSC101')."""
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 
                    p.id as prof_id,
                    p.name as prof_name,
                    d.abbrev as department,
                    (
                        SELECT COUNT(*)
                        FROM review r
                        JOIN professors_courses pc2 ON r.course_id = pc2.course_id
                        WHERE pc2.professor_id = p.id
                    ) as num_reviews
                FROM course c
                JOIN department_courses dc ON c.id = dc.course_id
                JOIN department d ON dc.department_id = d.id
                JOIN professors_courses pc ON c.id = pc.course_id
                JOIN professor p ON pc.professor_id = p.id
                WHERE c.course_code = :course_code
                """
            ),
            {"course_code": course_code.upper()}
        ).all()
        
    if not result:
        raise HTTPException(status_code=404, detail=f"Course {course_code} not found")
        
    professors = []
    for row in result:
        professors.append(
            Professor(
                id=str(row.prof_id),
                name=row.prof_name,
                department=row.department,
                num_reviews=row.num_reviews or 0,
                courses=[] 
            )
        )
            
    return professors

@router.get("/{course_code}/statistics")
async def get_course_aggregates(course_code: str) -> CourseAggregates:
    """Get aggregated statistics for a course by its code (e.g., 'ME101', 'CSC101')."""
    with db.engine.begin() as connection:
        # first get the course_id from the course_code
        course = connection.execute(
            sqlalchemy.text(
                """
                SELECT id 
                FROM course 
                WHERE course_code = :course_code
                """
            ),
            {"course_code": course_code.upper()}
        ).first()

        if not course:
            raise HTTPException(status_code=404, detail=f"Course {course_code} not found")

        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 
                    AVG(r.overall_rating) as avg_rating,
                    AVG(r.difficulty) as avg_difficulty,
                    AVG(r.workload_rating) as avg_workload,
                    COUNT(r.id) as total_reviews
                FROM review r
                WHERE r.course_id = :course_id
                """
            ),
            {"course_id": course.id}
        ).first()
        
        tags_query = """
            SELECT t.name AS tag_name
            FROM review r
            JOIN review_tags rt ON r.id = rt.review_id
            JOIN tag t ON rt.tag_id = t.id
            WHERE r.course_id = :course_id
            GROUP BY t.name
            ORDER BY COUNT(*) DESC
            LIMIT 5
        """
        tags = [row.tag_name for row in connection.execute(
            sqlalchemy.text(tags_query),
            {"course_id": course.id}).all()
        ]
    
        
    return CourseAggregates(
        average_rating=float(result.avg_rating or 0),
        average_difficulty=float(result.avg_difficulty or 0),
        average_workload=float(result.avg_workload or 0),
        total_reviews=result.total_reviews or 0,
        top_tags=tags
    )

@router.post("/", status_code=201, response_model=Course)
async def create_course(course: CourseCreate):
    with db.engine.begin() as connection:
        dept = connection.execute(
            sqlalchemy.text(
                "SELECT id FROM department WHERE abbrev = :dept"
            ),
            {"dept": course.department}
        ).first()
        
        if not dept:
            raise HTTPException(
                status_code=400,
                detail=f"Department {course.department} does not exist"
            )
            
        # create course
        course_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO course (course_code, name)
                VALUES (:course_code, :name)
                RETURNING id
                """
            ),
            {
                "course_code": course.course_code.upper(),
                "name": course.name,
            }
        ).scalar_one()
        
        # link course to department
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO department_courses (department_id, course_id)
                VALUES (:dept_id, :course_id)
                """
            ),
            {
                "dept_id": dept.id,
                "course_id": course_id
            }
        )
        
        return Course(
            course_id=course_id,
            name=course.name,
            department=course.department,
            professors=[]
        )
