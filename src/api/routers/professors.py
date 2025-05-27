from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
import sqlalchemy
from src.api.routers.models import Professor, Review, ProfessorDetails, NewProfessor
from src import database as db

router = APIRouter(prefix="/professors", tags=["professors"])

# TODO: allow metadata to be attaching courses to professor
# TODO: add endpoint for attaching courses to a professor
@router.get("/{professor_name}")
async def get_professor_details(professor_name: str) -> ProfessorDetails:
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
                    p.avg_workload,
                    p.avg_rating
                FROM professor p
                JOIN department d ON p.department_id = d.id
                WHERE p.name = :prof_name
                """
            ), {"prof_name": professor_name}
        ).first()
        if not prof_result:
            raise HTTPException(status_code=404, detail=f"Professor '{professor_name}' not found")

        # fetch all courses for this professor
        courses_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT
                    r.id as review_id,
                    c.id as course_id,
                    c.course_code,
                    c.name as course_name,
                    d.abbrev as department,
                    r.term,
                    r.difficulty,
                    r.overall_rating,
                    r.workload_rating,
                    r.comments,
                FROM review r
                JOIN course c ON r.course_id = c.id
                JOIN professors_courses pc ON c.id = pc.course_id
                JOIN professor p ON pc.professor_id = p.id
                JOIN department d ON c.department_id = d.id
                WHERE p.name = :prof_name
                """
            ), {"prof_name": professor_name}
        ).all()

        reviews_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT
                    r.id as review_id,
                    c.id as course_id,
                    c.course_code,
                    c.name as course_name,
                    d.abbrev as department,
                    r.term,
                    r.difficulty,
                    r.overall_rating,
                    r.workload_rating,
                    r.comments,
                    tag.name as tag_name
                    FROM review r
                    JOIN course c ON r.course_id = c.id
                    JOIN professors_courses pc ON c.id = pc.course_id
                    JOIN professor p ON pc.professor_id = p.id
                    JOIN department d ON c.department_id = d.id
                    JOIN review_tags ON r.id = review_tags.review_id
                    JOIN tag ON review_tags.tag_id = tag.id
                    WHERE p.name = :prof_name 
            """
            ), {"prof_name": professor_name}
        ).all()

        
        tags_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT t.name AS tag_name, COUNT(*) AS count
                FROM professor p
                JOIN professors_courses pc ON p.id = pc.professor_id
                JOIN review r ON r.course_id = pc.course_id
                JOIN review_tags rt ON rt.review_id = r.id
                JOIN tag t ON rt.tag_id = t.id
                WHERE p.id = :prof_id
                GROUP BY t.name
                ORDER BY count DESC
                LIMIT 10
                """
            ), {"prof_id": prof_result.id})
        
        courses = [
            {
                "course_id": int(row.course_id),  
                "name": row.course_name,
                "department": row.department,
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
        


        review_map = {}

        for row in reviews_result:
            review_id = row.review_id

            if review_id not in review_map:
                course = {
                    "course_id": int(row.course_id),
                    "name": row.course_name,
                    "department": row.department,
                }

                review_map[review_id] = Review(
                    review_id=str(review_id),
                    course=course,
                    term=row.term,
                    difficulty_rating=row.difficulty,
                    overall_rating=row.overall_rating,
                    workload_estimate=row.workload_rating,
                    tags=[],
                    comments=row.comments,
                )

            tag_name = row.tag_name
            if tag_name and tag_name not in review_map[review_id].tags:
                review_map[review_id].tags.append(tag_name)

        reviews = list(review_map.values())

        tags = [row.tag_name for row in tags_result]

        return ProfessorDetails(
            professor=professor,
            reviews=reviews,
            average_difficulty=float(prof_result.avg_difficulty or 0),
            average_workload=float(prof_result.avg_workload or 0),
            average_rating=float(prof_result.avg_rating or 0),
            most_common_tags=tags
        )

@router.post("/")
async def create_professor(professor: NewProfessor):
    """Create a new professor."""
    # first check if department exists
    try:    
        with db.engine.begin() as connection:
            dept_id = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT id FROM department WHERE abbrev = :dept
                    """    
                ), {'dept': professor.department}).scalar()
            
            if not dept_id:
                raise HTTPException(status_code=404, detail="Invalid department")
            
            prof_exists = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT 1
                    FROM professor
                    WHERE name = :name AND department_id = :dept_id
                    """
                ),
                {"dept_id": dept_id.id}
            ).first()

            if prof_exists:
                raise HTTPException(
                    status_code=409,
                    detail=f"Professor {professor.name} in department {professor.department} already exists"
                )

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
    except sqlalchemy.exc.IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail=f"Professor with name '{professor.name}' already exists"
        )
@router.post("/{professor_name}/courses")
async def attach_courses_to_professor(
    professor_name: str,
    course_codes: List[str]
) -> dict:
    """Attach courses to a professor by name. Course codes should be in the format 'ME101', 'CSC101', etc."""
    with db.engine.begin() as connection:
        # first verify the professor exists
        professor = connection.execute(
            sqlalchemy.text(
                "SELECT id FROM professor WHERE name = :prof_name"
            ),
            {"prof_name": professor_name}
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
                status_code=404,
                detail="One or more course codes could not be found"
            )
            
        # add the associations
        for course in courses:
            try:
                course_is_attached = connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT 1 
                        FROM professors_courses 
                        WHERE professor_id = :prof_id 
                        AND course_id = :course_id
                        """
                    ),
                    {
                        "prof_id": professor.id,
                        "course_id": course.id
                    }
                ).first()

                if course_is_attached:
                    print(f"Course {course.course_code} is already attached to professor {professor_name}, skipping...")
                    continue

                connection.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO professors_courses (professor_id, course_id)
                        VALUES (:prof_id, :course_id)
                        """
                    ),
                    {
                        "prof_id": professor.id,
                        "course_id": course.id
                    }
                )
            except sqlalchemy.exc.IntegrityError:
                print(f"Failed to attach course {course.course_code} to professor {professor_name}")
                continue

        return {"message": f"Finished processing {len(course_codes)} courses for professor '{professor_name}'"}

@router.get("/search/by-tags")
async def search_professors_by_tags(tags: List[str] = Query(None, description="List of tags to search for")) -> List[Professor]:
    """
    Search for professors based on review tags.
    Returns professors who have reviews with ANY of the specified tags.
    """
    if not tags:
        raise HTTPException(status_code=400, detail="At least one tag must be provided")
        
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                WITH tag_matches AS (
                    SELECT 
                        p.id,
                        p.name,
                        d.abbrev as department,
                        COUNT(DISTINCT t.name) as matching_tags,
                        COUNT(*) as tag_frequency,
                        p.total_reviews
                    FROM professor p
                    JOIN department d ON p.department_id = d.id
                    JOIN professors_courses pc ON p.id = pc.professor_id
                    JOIN review r ON r.course_id = pc.course_id
                    JOIN review_tags rt ON r.id = rt.review_id
                    JOIN tag t ON rt.tag_id = t.id
                    WHERE t.name = ANY(:tags)
                    GROUP BY p.id, p.name, d.abbrev, p.total_reviews
                    ORDER BY matching_tags DESC, tag_frequency DESC
                    LIMIT 20
                )
                SELECT 
                    tm.*,
                    array_agg(DISTINCT t.name) as matched_tags
                FROM tag_matches tm
                JOIN professors_courses pc ON tm.id = pc.professor_id
                JOIN review r ON r.course_id = pc.course_id
                JOIN review_tags rt ON r.id = rt.review_id
                JOIN tag t ON rt.tag_id = t.id
                WHERE t.name = ANY(:tags)
                GROUP BY tm.id, tm.name, tm.department, tm.matching_tags, tm.tag_frequency, tm.total_reviews
                """
            ),
            {"tags": tags}
        ).all()
        
        if not result:
            return []
            
        professors = []
        for row in result:
            professors.append(
                Professor(
                    id=str(row.id),
                    name=row.name,
                    department=row.department,
                    num_reviews=row.total_reviews or 0,
                    courses=[] 
                )
            )
            
        return professors
