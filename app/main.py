from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.routers import respondents, studies, assignments
from app.config import get_settings
from app.database import get_db
from app.models import Respondent

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


@app.post("/seed")
async def seed_database(db: AsyncSession = Depends(get_db)):
    """Seed the database with sample data (for demo purposes)."""
    import random
    from datetime import datetime, timedelta, date
    from decimal import Decimal
    from app.models import Respondent, Study, ScreenerCriteria, StudyAssignment

    # Check if already seeded
    result = await db.execute(select(func.count(Respondent.id)))
    if result.scalar() > 10:
        return {"message": "Database already seeded", "seeded": False}

    # Sample data
    FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
                   "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
                   "Thomas", "Sarah", "Charles", "Karen", "Daniel", "Nancy", "Matthew", "Lisa"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                  "Rodriguez", "Martinez", "Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Jackson"]
    STATES = ["NY", "CA", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI", "NJ", "VA", "WA", "AZ", "MA", "CO"]
    INCOMES = ["Under 25k", "25k-50k", "50k-75k", "75k-100k", "100k-150k", "150k+"]
    GENDERS = ["male", "female", "non-binary"]
    OCCUPATIONS = ["Software Engineer", "Teacher", "Nurse", "Marketing Manager", "Sales Rep",
                   "Accountant", "Designer", "Data Analyst", "Product Manager", "Consultant"]

    # Create 100 respondents
    respondents = []
    for i in range(100):
        r = Respondent(
            first_name=random.choice(FIRST_NAMES),
            last_name=random.choice(LAST_NAMES),
            email=f"user{i}@example.com",
            phone=f"{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
            city="City",
            state=random.choice(STATES),
            zip_code=str(random.randint(10000, 99999)),
            age=random.randint(21, 65),
            gender=random.choice(GENDERS),
            household_income=random.choice(INCOMES),
            occupation=random.choice(OCCUPATIONS),
            is_active=True,
        )
        db.add(r)
        respondents.append(r)

    await db.flush()

    # Create studies
    study_data = [
        {"title": "Coffee Consumption Habits", "client": "Starbucks", "method": "focus_group", "target": 12,
         "incentive": Decimal("150"), "criteria": [("age", "between", [25, 45]), ("household_income", "in", ["75k-100k", "100k-150k"])]},
        {"title": "Gen Z Shopping Preferences", "client": "Nike", "method": "idi", "target": 20,
         "incentive": Decimal("125"), "criteria": [("age", "between", [18, 27])]},
        {"title": "Electric Vehicle Interest", "client": "Tesla", "method": "focus_group", "target": 15,
         "incentive": Decimal("200"), "criteria": [("household_income", "in", ["100k-150k", "150k+"]), ("age", "gte", 30)]},
        {"title": "Streaming Service Usage", "client": "Netflix", "method": "survey", "target": 50,
         "incentive": Decimal("25"), "criteria": [("age", "between", [18, 55])]},
        {"title": "Mobile Banking Experience", "client": "Chase", "method": "idi", "target": 25,
         "incentive": Decimal("100"), "criteria": [("age", "between", [21, 60])]},
        {"title": "Fitness App Feedback", "client": "Peloton", "method": "focus_group", "target": 10,
         "incentive": Decimal("175"), "criteria": [("age", "between", [25, 45]), ("household_income", "in", ["75k-100k", "100k-150k", "150k+"])]},
    ]

    statuses = ["draft", "recruiting", "recruiting", "in_field", "in_field", "completed"]
    studies = []

    for i, sd in enumerate(study_data):
        study = Study(
            title=sd["title"],
            client_name=sd["client"],
            methodology=sd["method"],
            target_count=sd["target"],
            incentive_amount=sd["incentive"],
            status=statuses[i],
            start_date=date.today() - timedelta(days=random.randint(0, 30)) if statuses[i] != "draft" else None,
        )
        db.add(study)
        await db.flush()

        for field, op, val in sd["criteria"]:
            crit = ScreenerCriteria(study_id=study.id, field_name=field, operator=op, value=val)
            db.add(crit)

        studies.append(study)

    await db.flush()

    # Create assignments for non-draft studies
    assignment_count = 0
    for study in studies:
        if study.status == "draft":
            continue
        assigned = random.sample(respondents, min(random.randint(5, 15), len(respondents)))
        for resp in assigned:
            status = random.choice(["invited", "confirmed", "completed"] if study.status == "completed" else ["invited", "confirmed"])
            assignment = StudyAssignment(
                study_id=study.id,
                respondent_id=resp.id,
                status=status,
                confirmed_at=datetime.utcnow() if status in ["confirmed", "completed"] else None,
                completed_at=datetime.utcnow() if status == "completed" else None,
            )
            db.add(assignment)
            assignment_count += 1

    await db.flush()

    return {
        "message": "Database seeded successfully",
        "seeded": True,
        "respondents": len(respondents),
        "studies": len(studies),
        "assignments": assignment_count,
    }
