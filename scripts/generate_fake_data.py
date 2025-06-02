import sqlalchemy
import os
import dotenv
from faker import Faker
import random
import numpy as np

dotenv.load_dotenv()
def database_connection_url():
    dotenv.load_dotenv()
    DB_USER = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER = os.environ.get("POSTGRES_SERVER")
    DB_PORT = os.environ.get("POSTGRES_PORT")
    DB_NAME = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)

departments = [
    'Computer Science',
    'Computer Engineering',
    'Ethnic Studies',
    'Mathematics',
    'English'
]
tags = [
    'compsci',
    'chill',
    'async',
    'uploads slides',
    'flexible attendance policy',
    'boring',
    'lame',
    'fun',
    'clear lectures',
    'fair grading',
    'good'
]

with engine.begin() as conn:
    conn.execute(sqlalchemy.text("""
    DROP TABLE IF EXISTS courses;
    DROP TABLE IF EXISTS professors
    DROP TABLE IF EXISTS reviews
    DROP TABLE IF EXISTS departments;

    

    """))
