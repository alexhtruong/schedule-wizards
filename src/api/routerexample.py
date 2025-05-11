from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

@router.post("/hi")
def test():
    pass

# NOTE THIS WILL BE USED TO ORGANIZE API ROUTES