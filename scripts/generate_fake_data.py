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

schools = [
    'California Polytechnic University',
    'University of Washington',
    'University of Arizona',
    'San Jose State University'
]

with engine.begin() as conn:
    conn.execute(sqlalchemy.text("""
    DROP TABLE IF EXISTS course;
    DROP TABLE IF EXISTS professor;
    DROP TABLE IF EXISTS review;
    DROP TABLE IF EXISTS department;
    DROP TABLE IF EXISTS school;
    DROP TABLE IF EXISTS tag;
    DROP TABLE IF EXISTS department_courses;
    DROP TABLE IF EXISTS professors_courses;
    DROP TABLE IF EXISTS review_tags;
    DROP TABLE IF EXISTS student;

    CREATE TABLE
        school (
            id int generated always as identity not null PRIMARY KEY,
            name text not null,
            city text not null,
            state text not null,
            country text not null
        );

    CREATE TABLE
        department (
            id int generated always as identify not null PRIMARY KEY,
            name text not null,
            abbrev text not null,
            school_id int not null references school(id)
        );

    CREATE TABLE
        professor (
            id int generated always as identify not null PRIMARY KEY,
            name text not null,
            avg_rating float not null,
            classes_taught int,
            department_id int not null references department(id),
            total_reviews int not null,
            avg_difficulty int not null,
            avg_workload int not null
        );

    CREATE TABLE
        student (
            id int generated always as identity not null PRIMARY KEY,
            major text not null,
            dept_id int references department(id),
            first_name text not null,
            last_name text not null,
            email text not null,
            review_count int
        );

    CREATE TABLE
        course (
            id int generated always as identity not null PRIMARY KEY,
            course_code text not null,
            name text not null,
            avg_workload int not null,
            avg_rating float not null,
            department_id int references department(id)

        );

    CREATE TABLE
        review (
            id int generated always as identity not null PRIMARY KEY,
            course_id int not null references course(id),
            term text not null,
            difficulty text not null,
            overall_rating int not null,
            workload_rating int not null,
            comments text not null
        );

    CREATE TABLE
        tag (
            id int generated always as identity not null PRIMARY KEY,
            name text not null
        );

    CREATE TABLE
        review_tags (
            review_id int not null references review(id),
            tag_id int not null references tag(id)
        );

    CREATE TABLE
        professors_courses (
            professor_id int not null references professor(id),
            course_id int not null references course(id)
        );

    CREATE TABLE
        department_courses (
            department_id int not null references department(id),
            course_id int not null references course(id)
        );
    """))

    # Populate initial tables:
    for school in schools:
        conn.execute(sqlalchemy.text("""
        INSERT INTO school (name) VALUES (:name);
        """), {"name": school})
