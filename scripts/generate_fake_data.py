import sqlalchemy
import os
import dotenv
from faker import Faker
import random
import numpy as np

dotenv.load_dotenv()
def database_connection_url():
    DB_USER = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER = os.environ.get("POSTGRES_SERVER")
    DB_PORT = os.environ.get("POSTGRES_PORT")
    DB_NAME = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)
fake = Faker()
num_professors = 500
num_students = 500
num_reviews = 249605

departments = [
    ['Computer Science', 'CSC'],
    ['Computer Engineering', 'CPE'],
    ['Ethnic Studies', 'ES'],
    ['Mathematics', 'MAT'],
    ['English', 'ENG']
]

courses = [
    ['Data Structures', 'CSC202'],
    ['Fundamentals of Computer Science', "CSC101"],
    ['Project-Based Object-Oriented Programming and Design', 'CSC203'],
    ['Discrete Structures', 'CSC248'],
    ['Introduction to Software Engineering', 'CSC307'],
    ['Introduction to Computer Security', 'CSC321'],
    ['Design and Analysis of Algorithms', 'CSC349'],
    ['Systems Programming', 'CSC357'],
    ['Introduction to Database Systems', 'CSC365'],
    ['Introduction to Computer Organization', 'CPE225'],
    ['Asian American Histroy', 'ES251'],
    ['Calculus III', 'MAT143'],
    ['Calculus II', 'MAT142'],
    ['Calculus I', 'MAT141'],
    ['Linear Algebra I', 'MAT206'],
    ['Writing and Rhetoric', 'ENG143']
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

review_terms = ['Fall 2023', 'Winter 2024', 'Spring 2024', 'Fall 2024']

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
            id int generated always as identity not null PRIMARY KEY,
            name text not null,
            abbrev text not null,
            school_id int not null references school(id)
        );

    CREATE TABLE
        professor (
            id int generated always as identity not null PRIMARY KEY,
            name text not null,
            department_id int not null references department(id)
        );

    CREATE TABLE
        student (
            id int generated always as identity not null PRIMARY KEY,
            major text not null,
            dept_id int references department(id),
            first_name text not null,
            last_name text not null,
            email text not null
        );

    CREATE TABLE
        course (
            id int generated always as identity not null PRIMARY KEY,
            course_code text not null,
            name text not null,
            department_id int references department(id)

        );

    CREATE TABLE
        review (
            id int generated always as identity not null PRIMARY KEY,
            course_id int not null references course(id),
            term text not null,
            difficulty int not null,
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

    # Insert Cal Poly
    conn.execute(sqlalchemy.text("""
        INSERT INTO school (name, city, state, country)
        VALUES (:name, :city, :state, :country);
    """), {
        "name": "California Polytechnic University",
        "city": "San Luis Obispo",
        "state": "California",
        "country": "United States of America"
    })

    school_id = conn.execute(sqlalchemy.text("""
        SELECT id FROM school WHERE name = :name
    """), {"name": "California Polytechnic University"}).scalar_one()

    # Insert departments
    for department in departments:
        conn.execute(sqlalchemy.text("""
            INSERT INTO department (name, abbrev, school_id)
            VALUES (:name, :abbrev, :school_id);
        """), {
            "name": department[0],
            "abbrev": department[1],
            "school_id": school_id
        })

    department_ids = conn.execute(sqlalchemy.text("""
        SELECT id FROM department
    """)).scalars().all()

    # Insert professors
    for professor in range(num_professors):
        conn.execute(sqlalchemy.text("""
            INSERT INTO professor (name, department_id)
            VALUES (:name, :department_id);
        """), {
            "name": fake.name(),
            "department_id": np.random.choice(department_ids)
        })

    professor_ids = conn.execute(sqlalchemy.text("""
        SELECT id FROM professor
    """)).scalars().all()

    # Insert courses
    for course in courses:
        conn.execute(sqlalchemy.text("""
            INSERT INTO course (course_code, name, department_id)
            VALUES (:course_code, :name, :department_id);
        """), {
            "course_code": course[1],
            "name": course[0],
            "department_id": None
        })

    course_ids = conn.execute(sqlalchemy.text("""
        SELECT id FROM course
    """)).scalars().all()

    for tag in tags:
        conn.execute(sqlalchemy.text("""
            INSERT INTO tag (name)
            VALUES (:name);
        """), {
            "name": tag
        })

    # Insert students
    for student in range(num_students):
        conn.execute(sqlalchemy.text("""
            INSERT INTO student (major, dept_id, first_name, last_name, email)
            VALUES (:major, :dept_id, :first_name, :last_name, :email);
        """), {
            "major": np.random.choice(departments)[0],
            "dept_id": None,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email()
        })

    for review in range(num_reviews):
        result = conn.execute(sqlalchemy.text("""
            INSERT INTO review (course_id, term, difficulty, overall_rating, workload_rating, comments)
            VALUES (:course_id, :term, :difficulty, :overall_rating, :workload_rating, :comments)
            RETURNING id
        """), {
            "course_id": np.random.choice(course_ids),
            "term": np.random.choice(review_terms),
            "difficulty": np.random.randint(0,6),
            "overall_rating": np.random.randint(0,6),
            "workload_rating": np.random.randint(0,200),
            "comments": fake.sentence(nb_words=12)
        })