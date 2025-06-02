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
    DROP TABLE IF EXISTS course;
    DROP TABLE IF EXISTS professor;
    DROP TABLE IF EXISTS review;
    DROP TABLE IF EXISTS department;
    DROP TABLE IF EXISTS school;

    CREATE TABLE
        school (
            id int generated always as identity not null PRIMARY KEY,
            name text not null,
            city text not null,
            state text not null,
            country text not null
        );

    """))
