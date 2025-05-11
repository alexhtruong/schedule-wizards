from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlalchemy
from src import database as db

router = APIRouter(prefix="/courses", tags=["courses"])

class Professor(BaseModel):
    name: str
    professor_id: int

class Course(BaseModel):
    course_id: int
    name: str
    department: str
    professors: List[Professor]

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
            c.id as course_id,
            c.name,
            d.abbrev as department,
            p.id as prof_id,
            p.name as prof_name
        FROM course c
        JOIN department_courses dc ON c.id = dc.course_id
        JOIN department d ON dc.department_id = d.id
        JOIN professors_courses pc ON c.id = pc.course_id
        JOIN professor p ON pc.professor_id = p.id
        WHERE 1=1
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
        courses_dict[row.course_id].professors.append(
            Professor(name=row.prof_name, professor_id=str(row.prof_id))
        )
            
    return list(courses_dict.values())

@router.get("/{course_id}")
async def get_course(course_id: str) -> Course:
    """Get a specific course's details."""
    with db.engine.begin() as conn:
        result = conn.execute(
            sqlalchemy.text(
                """
                SELECT 
                    c.id as course_id,
                    c.name,
                    d.abbrev as department,
                    p.id as prof_id,
                    p.name as prof_name
                FROM course c
                JOIN department_courses dc ON c.id = dc.course_id
                JOIN department d ON dc.department_id = d.id
                JOIN professors_courses pc ON c.id = pc.course_id
                JOIN professor p ON pc.professor_id = p.id
                WHERE c.id = :course_id
                """
            ),
            {"course_id": course_id}
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
            courses_dict[row.course_id].professors.append(
                Professor(name=row.prof_name, professor_id=str(row.prof_id))
            )
 
        if len(courses_dict) != 1:
            raise HTTPException(
                status_code=500,
                detail="Expected exactly one course, found multiple"
            )
    
        return list(courses_dict.values())[0]


@router.get("/{course_id}/professors")
async def get_course_professors(course_id: str) -> List[Professor]:
    """Get professors teaching a specific course."""
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 
                    c.id as course_id,
                    c.name,
                    d.abbrev as department,
                    p.id as prof_id,
                    p.name as prof_name
                FROM course c
                JOIN department_courses dc ON c.id = dc.course_id
                JOIN department d ON dc.department_id = d.id
                JOIN professors_courses pc ON c.id = pc.course_id
                JOIN professor p ON pc.professor_id = p.id
                WHERE c.id = :course_id
                """
            ),
            {"course_id": course_id}
        ).all()
        
    if not result:
        raise HTTPException(status_code=404, detail="Course not found")
        
    course_data = None
    for row in result:
        if not course_data:
            course_data = Course(
                course_id=row.course_id,
                name=row.name,
                department=row.department,
                professors=[]
            )
        course_data.professors.append(
            Professor(name=row.prof_name, professor_id=str(row.prof_id))
        )
            
    if not course_data:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return course_data

@router.get("/{course_id}/statistics")
async def get_course_aggregates(course_id: str) -> CourseAggregates:
    """Get aggregated statistics for a course."""
    with db.engine.begin() as connection:
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
            {"course_id": course_id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Course not found")
        
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
            {"course_id": course_id}).all()
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
            
        # Create course
        course_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO course (course_code, name)
                VALUES (:course_code, :name)
                RETURNING id
                """
            ),
            {
                "course_code": course.course_code,
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
