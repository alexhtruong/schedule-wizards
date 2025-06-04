import sqlalchemy
import os
import sys
import dotenv
from faker import Faker
import numpy as np
from pathlib import Path
import asyncio

# Add the project root to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

try:
    from src.api.routers.stats import refresh_all_statistics
except ImportError as e:
    print(f"Failed to import refresh_all_statistics: {e}")
    refresh_all_statistics = lambda: None  # Dummy function if import fails

# dotenv.load_dotenv()
dotenv.load_dotenv(dotenv_path="default.env")
db_url = os.getenv("POSTGRES_URI")

# def database_connection_url():
#     DB_USER = os.environ.get("POSTGRES_USER")
#     DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
#     DB_SERVER = os.environ.get("POSTGRES_SERVER")
#     DB_PORT = os.environ.get("POSTGRES_PORT")
#     DB_NAME = os.environ.get("POSTGRES_DB")
#     return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

engine = sqlalchemy.create_engine(db_url, use_insertmanyvalues=True)
fake = Faker()
# Adjust numbers for larger dataset
num_professors = 5000  # 5k professors
num_reviews = 1000000  # 1M reviews
num_reviews_per_batch = 10000  # Insert reviews in batches

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
    DROP TABLE IF EXISTS course CASCADE;
    DROP TABLE IF EXISTS professor CASCADE;
    DROP TABLE IF EXISTS review CASCADE;
    DROP TABLE IF EXISTS department CASCADE;
    DROP TABLE IF EXISTS school CASCADE;
    DROP TABLE IF EXISTS tag CASCADE;
    DROP TABLE IF EXISTS department_courses CASCADE;
    DROP TABLE IF EXISTS professors_courses CASCADE;
    DROP TABLE IF EXISTS review_tags CASCADE;

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
            department_id int not null references department(id),
            avg_workload int,
            avg_difficulty float,
            avg_rating float,
            total_reviews int
        );

    CREATE TABLE
        course (
            id int generated always as identity not null PRIMARY KEY,
            course_code text not null,
            name text not null,
            department_id int references department(id),
            avg_workload int,
            avg_rating float
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
        print(f"inserting department: {department}")
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
        print(f"inserting professor: {professor}")
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
        print(f"inserting course: {course}")
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
        print(f"inserting tag: {tag}")
        conn.execute(sqlalchemy.text("""
            INSERT INTO tag (name)
            VALUES (:name);
        """), {
            "name": tag
        })

    # Generate reviews and get their IDs for review_tags
    review_ids = []
    for batch in range(0, num_reviews, num_reviews_per_batch):
        print(f"Inserting reviews batch {batch // num_reviews_per_batch + 1} of {num_reviews // num_reviews_per_batch}")
        
        review_batch = [{
            "course_id": np.random.choice(course_ids),
            "term": np.random.choice(review_terms),
            "difficulty": np.random.randint(0,6),
            "overall_rating": np.random.randint(0,6),
            "workload_rating": np.random.randint(0,200),
            "comments": fake.sentence(nb_words=12)
        } for _ in range(min(num_reviews_per_batch, num_reviews - batch))]
        
        for review in review_batch:
            result = conn.execute(sqlalchemy.text("""
                INSERT INTO review (course_id, term, difficulty, overall_rating, workload_rating, comments)
                VALUES (:course_id, :term, :difficulty, :overall_rating, :workload_rating, :comments)
                RETURNING id;
            """), review).scalar_one()
            review_ids.append(result)

    print("Linking departments to courses...")
    # Link departments to their courses based on course code prefix
    fetched_courses = conn.execute(sqlalchemy.text("""
        SELECT id, course_code FROM course
    """)).fetchall()
    for course_id, course_code in fetched_courses:
        dept_abbrev = course_code[:3]  # Get department prefix (e.g., 'CSC' from 'CSC101')
        dept_id = conn.execute(sqlalchemy.text("""
            SELECT id FROM department WHERE abbrev = :abbrev
        """), {"abbrev": dept_abbrev}).scalar()
        
        if dept_id:
            conn.execute(sqlalchemy.text("""
                INSERT INTO department_courses (department_id, course_id)
                VALUES (:dept_id, :course_id)
            """), {"dept_id": dept_id, "course_id": course_id})
            
            # Also update the course's department_id
            conn.execute(sqlalchemy.text("""
                UPDATE course 
                SET department_id = :dept_id 
                WHERE id = :course_id
            """), {"dept_id": dept_id, "course_id": course_id})

    print("Linking professors to courses...")
    # Assign professors to courses (each professor teaches 2-5 courses)
    for prof_id in professor_ids:
        num_courses = np.random.randint(2, 6)
        # Get random courses from the professor's department
        dept_id = conn.execute(sqlalchemy.text("""
            SELECT department_id FROM professor WHERE id = :prof_id
        """), {"prof_id": prof_id}).scalar()
        
        dept_courses = conn.execute(sqlalchemy.text("""
            SELECT id FROM course WHERE department_id = :dept_id
        """), {"dept_id": dept_id}).scalars().all()
        
        if dept_courses:
            selected_courses = np.random.choice(dept_courses, 
                                             size=min(num_courses, len(dept_courses)), 
                                             replace=False)
            for course_id in selected_courses:
                conn.execute(sqlalchemy.text("""
                    INSERT INTO professors_courses (professor_id, course_id)
                    VALUES (:prof_id, :course_id)
                """), {"prof_id": prof_id, "course_id": course_id})

    print("Adding tags to reviews...")
    # Add 1-3 random tags to each review
    tag_ids = conn.execute(sqlalchemy.text("SELECT id FROM tag")).scalars().all()
    for review_id in review_ids:
        num_tags = np.random.randint(1, 4)
        selected_tags = np.random.choice(tag_ids, size=num_tags, replace=False)
        for tag_id in selected_tags:
            conn.execute(sqlalchemy.text("""
                INSERT INTO review_tags (review_id, tag_id)
                VALUES (:review_id, :tag_id)
            """), {"review_id": review_id, "tag_id": tag_id})

    # print("Refreshing statistics...")
    # asyncio.run(refresh_all_statistics())
