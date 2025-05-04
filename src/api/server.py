from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


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


@app.get("/")
async def root():
    return {"message": "wizard api is up"}
