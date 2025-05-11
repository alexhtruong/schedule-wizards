from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from src.api.routers import courses, professors, reviews, departments

app = FastAPI(
    title="Schedule Wizards",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PATCH", "PUT" "OPTIONS"],
    allow_headers=["*"],
)

# Include our routers
app.include_router(courses.router)
app.include_router(professors.router)
app.include_router(reviews.router)
app.include_router(departments.router)

@app.get("/")
async def root():
    return {"message": "wizard api is up"}

