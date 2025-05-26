from fastapi import APIRouter, HTTPException
import sqlalchemy
from src.api.routers.models import ReviewCreate
from src import database as db

router = APIRouter(prefix="/stats", tags=["stats"])

# cron job running every 24 hours
@router.post("/refresh")
async def refresh_all_statistics():
    """Update statistics for all courses and professors."""
    with db.engine.begin() as connection:
        try:
            # update all course statistics
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
                    """
                )
            )

            # update all professor statistics
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
                    """
                )
            )

            return {
                "message": "Statistics refreshed successfully"
            }

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=500,
                detail="Error refreshing statistics"
            ) from e