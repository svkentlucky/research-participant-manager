from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import respondents, studies, assignments
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Research Participant Manager",
    description="API for managing qualitative research respondents, studies, and participant matching",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(respondents.router, prefix="/api/respondents", tags=["Respondents"])
app.include_router(studies.router, prefix="/api/studies", tags=["Studies"])
app.include_router(assignments.router, prefix="/api/assignments", tags=["Assignments"])


@app.get("/")
async def root():
    return {"message": "Research Participant Manager API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
