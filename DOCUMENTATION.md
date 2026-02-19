# Research Participant Manager API - Technical Documentation

> A production-ready FastAPI + PostgreSQL REST API for managing qualitative research respondents, studies, and participant matching.

**Author:** Kent Lucky Buhawe
**Created:** February 2026
**Stack:** Python 3.9+, FastAPI, PostgreSQL, SQLAlchemy 2.0, Alembic, Pydantic v2

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database Schema](#database-schema)
3. [API Endpoints](#api-endpoints)
4. [Core Features](#core-features)
5. [Code Examples](#code-examples)
6. [Performance Considerations](#performance-considerations)
7. [Deployment & Migrations](#deployment--migrations)
8. [Testing](#testing)

---

## Architecture Overview

### Project Structure

```
research-participant-manager/
├── alembic/                    # Database migrations
│   ├── versions/
│   │   ├── 001_create_respondents.py
│   │   ├── 002_create_studies.py
│   │   ├── 003_create_screener_criteria.py
│   │   └── 004_create_study_assignments.py
│   └── env.py
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Environment-based configuration
│   ├── database.py             # Async database connection & sessions
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── respondent.py
│   │   ├── study.py
│   │   ├── screener_criteria.py
│   │   └── study_assignment.py
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── respondent.py
│   │   ├── study.py
│   │   └── study_assignment.py
│   ├── routers/                # API route handlers
│   │   ├── respondents.py
│   │   ├── studies.py
│   │   └── assignments.py
│   └── services/               # Business logic layer
│       ├── respondent_service.py
│       └── matching_service.py
├── scripts/
│   └── seed_data.py            # Database seeding script
├── tests/
│   ├── conftest.py
│   ├── test_respondents.py
│   ├── test_studies.py
│   └── test_matching.py
├── docker-compose.yml
├── requirements.txt
└── alembic.ini
```

### Design Principles

1. **Separation of Concerns**: Models → Schemas → Services → Routers
2. **Async First**: All database operations use async/await for better concurrency
3. **Type Safety**: Full type hints with Pydantic validation
4. **Clean Migrations**: Each table has its own versioned migration file

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│   respondents   │       │     studies     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ first_name      │       │ title           │
│ last_name       │       │ client_name     │
│ email (UNIQUE)  │       │ methodology     │
│ phone           │       │ target_count    │
│ city            │       │ incentive_amount│
│ state           │       │ status          │
│ zip_code        │       │ start_date      │
│ age             │       │ end_date        │
│ gender          │       │ created_at      │
│ ethnicity       │       └────────┬────────┘
│ household_income│                │
│ occupation      │                │ 1:N
│ is_active       │                │
│ created_at      │       ┌────────▼────────┐
│ updated_at      │       │screener_criteria│
└────────┬────────┘       ├─────────────────┤
         │                │ id (PK)         │
         │                │ study_id (FK)   │
         │                │ field_name      │
         │ M:N            │ operator        │
         │                │ value (JSONB)   │
         │                │ created_at      │
┌────────▼────────┐       └─────────────────┘
│study_assignments│
├─────────────────┤
│ id (PK)         │
│ study_id (FK)   │◄──────────────┘
│ respondent_id   │
│ status          │
│ invited_at      │
│ confirmed_at    │
│ completed_at    │
│ notes           │
└─────────────────┘
  UNIQUE(study_id, respondent_id)
```

### Table Details

#### respondents
| Column | Type | Constraints | Index |
|--------|------|-------------|-------|
| id | SERIAL | PRIMARY KEY | ✓ |
| first_name | VARCHAR(100) | NOT NULL | |
| last_name | VARCHAR(100) | NOT NULL | |
| email | VARCHAR(255) | NOT NULL, UNIQUE | ✓ |
| phone | VARCHAR(20) | | |
| city | VARCHAR(100) | | |
| state | VARCHAR(2) | | ✓ |
| zip_code | VARCHAR(10) | | |
| age | INTEGER | | ✓ |
| gender | VARCHAR(20) | | |
| ethnicity | VARCHAR(50) | | |
| household_income | VARCHAR(50) | | ✓ |
| occupation | VARCHAR(100) | | |
| is_active | BOOLEAN | DEFAULT true | ✓ |
| created_at | TIMESTAMP | NOT NULL | |
| updated_at | TIMESTAMP | NOT NULL | |

**Composite Indexes:**
- `ix_respondents_state_age` - For geographic + age filtering
- `ix_respondents_active_state` - For active respondent queries

#### studies
| Column | Type | Constraints | Index |
|--------|------|-------------|-------|
| id | SERIAL | PRIMARY KEY | ✓ |
| title | VARCHAR(255) | NOT NULL | |
| client_name | VARCHAR(255) | NOT NULL | ✓ |
| methodology | VARCHAR(50) | NOT NULL | |
| target_count | INTEGER | NOT NULL | |
| incentive_amount | DECIMAL(10,2) | | |
| status | VARCHAR(20) | DEFAULT 'draft' | ✓ |
| start_date | DATE | | |
| end_date | DATE | | |
| created_at | TIMESTAMP | NOT NULL | |

**Methodology Values:** `focus_group`, `idi`, `survey`, `ethnography`
**Status Values:** `draft`, `recruiting`, `in_field`, `completed`

#### screener_criteria
| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PRIMARY KEY |
| study_id | INTEGER | FK → studies.id, ON DELETE CASCADE |
| field_name | VARCHAR(50) | NOT NULL |
| operator | VARCHAR(20) | NOT NULL |
| value | JSONB | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |

**Operators:** `eq`, `neq`, `gte`, `lte`, `in`, `between`

**JSONB Value Examples:**
```json
// Equal to string
{"field_name": "state", "operator": "eq", "value": "NY"}

// In list
{"field_name": "state", "operator": "in", "value": ["NY", "CA", "TX"]}

// Between (range)
{"field_name": "age", "operator": "between", "value": [25, 45]}

// Greater than or equal
{"field_name": "age", "operator": "gte", "value": 21}
```

#### study_assignments
| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PRIMARY KEY |
| study_id | INTEGER | FK → studies.id, ON DELETE CASCADE |
| respondent_id | INTEGER | FK → respondents.id, ON DELETE CASCADE |
| status | VARCHAR(20) | DEFAULT 'invited' |
| invited_at | TIMESTAMP | NOT NULL |
| confirmed_at | TIMESTAMP | |
| completed_at | TIMESTAMP | |
| notes | TEXT | |

**Unique Constraint:** `(study_id, respondent_id)` - Prevents duplicate assignments

**Status Values:** `invited`, `confirmed`, `completed`, `no_show`, `rejected`

---

## API Endpoints

### Base URL
```
http://localhost:8001/api
```

### Respondents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/respondents` | Create a new respondent |
| `GET` | `/respondents` | List respondents with filters |
| `GET` | `/respondents/{id}` | Get single respondent |
| `PUT` | `/respondents/{id}` | Update respondent |
| `DELETE` | `/respondents/{id}` | Soft delete (set is_active=false) |

**Query Parameters for GET /respondents:**
| Parameter | Type | Description |
|-----------|------|-------------|
| limit | int | Results per page (default: 20, max: 100) |
| offset | int | Pagination offset |
| state | string | Filter by state code |
| age_min | int | Minimum age filter |
| age_max | int | Maximum age filter |
| household_income | string | Filter by income bracket |
| gender | string | Filter by gender |
| is_active | bool | Filter by active status |

### Studies

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/studies` | Create study with criteria |
| `GET` | `/studies` | List studies with filters |
| `GET` | `/studies/{id}` | Get study with criteria & counts |
| `PUT` | `/studies/{id}` | Update study |
| `GET` | `/studies/{id}/match` | **Find matching respondents** |
| `POST` | `/studies/{id}/assign` | Assign respondents to study |

### Assignments

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/assignments/{id}` | Get assignment details |
| `PATCH` | `/assignments/{id}` | Update assignment status |

---

## Core Features

### 1. Smart Matching Engine

The matching service (`app/services/matching_service.py`) dynamically builds SQL queries based on JSONB criteria:

```python
class MatchingService:
    async def find_matching_respondents(
        self,
        study_id: int,
        exclude_assigned: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Respondent], int]:
        # Build base query for active respondents
        query = select(Respondent).where(Respondent.is_active == True)

        # Exclude already assigned respondents
        if exclude_assigned:
            assigned_subquery = (
                select(StudyAssignment.respondent_id)
                .where(StudyAssignment.study_id == study_id)
            )
            query = query.where(Respondent.id.not_in(assigned_subquery))

        # Apply each criterion dynamically
        for criterion in criteria_list:
            condition = self._build_condition(criterion)
            if condition is not None:
                query = query.where(condition)
```

**Supported Operators:**

| Operator | SQL Equivalent | Example |
|----------|---------------|---------|
| `eq` | `=` | `state = 'NY'` |
| `neq` | `!=` | `state != 'TX'` |
| `gte` | `>=` | `age >= 25` |
| `lte` | `<=` | `age <= 45` |
| `in` | `IN (...)` | `state IN ('NY', 'CA')` |
| `between` | `BETWEEN` | `age BETWEEN 25 AND 45` |

### 2. Async Database Sessions

All database operations use SQLAlchemy's async engine:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,  # Verify connections before use
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### 3. Pydantic Validation

Request/response validation with type safety:

```python
class RespondentCreate(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    age: Optional[int] = Field(None, ge=18, le=120)
    state: Optional[str] = Field(None, max_length=2)
    household_income: Optional[str] = Field(None, max_length=50)

    class Config:
        from_attributes = True  # Enable ORM mode
```

---

## Code Examples

### Example 1: SQL Query with JOIN and Aggregation

```sql
-- Get assignment statistics per study
SELECT
    s.id,
    s.title,
    s.client_name,
    s.target_count,
    COUNT(sa.id) as total_assigned,
    SUM(CASE WHEN sa.status = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
    SUM(CASE WHEN sa.status = 'completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN sa.status = 'no_show' THEN 1 ELSE 0 END) as no_shows
FROM studies s
LEFT JOIN study_assignments sa ON sa.study_id = s.id
WHERE s.status = 'in_field'
GROUP BY s.id, s.title, s.client_name, s.target_count
ORDER BY s.created_at DESC;
```

### Example 2: Complex Matching Query

```sql
-- Find respondents matching multiple criteria
-- Criteria: Age 25-45, State in (NY, CA), Income >= 75k
SELECT r.*
FROM respondents r
WHERE r.is_active = true
  AND r.age BETWEEN 25 AND 45
  AND r.state IN ('NY', 'CA')
  AND r.household_income IN ('75k-100k', '100k-150k', '150k+')
  AND r.id NOT IN (
      SELECT respondent_id
      FROM study_assignments
      WHERE study_id = 5
  )
ORDER BY r.created_at DESC
LIMIT 50;
```

### Example 3: API Endpoint Implementation

```python
@router.get("/{study_id}/match", response_model=dict)
async def find_matching_respondents(
    study_id: int,
    exclude_assigned: bool = Query(True),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Find respondents matching the study's screener criteria."""
    # Verify study exists
    result = await db.execute(select(Study).where(Study.id == study_id))
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Use service layer for business logic
    service = MatchingService(db)
    respondents, total = await service.find_matching_respondents(
        study_id=study_id,
        exclude_assigned=exclude_assigned,
        limit=limit,
        offset=offset,
    )

    return {
        "items": [RespondentResponse.model_validate(r) for r in respondents],
        "total": total,
        "limit": limit,
        "offset": offset,
        "study_id": study_id,
    }
```

---

## Performance Considerations

### Indexes Strategy

```sql
-- Single column indexes for common filters
CREATE INDEX ix_respondents_email ON respondents(email);
CREATE INDEX ix_respondents_state ON respondents(state);
CREATE INDEX ix_respondents_age ON respondents(age);
CREATE INDEX ix_respondents_household_income ON respondents(household_income);
CREATE INDEX ix_respondents_is_active ON respondents(is_active);

-- Composite indexes for common query patterns
CREATE INDEX ix_respondents_state_age ON respondents(state, age);
CREATE INDEX ix_respondents_active_state ON respondents(is_active, state);
CREATE INDEX ix_studies_status_start ON studies(status, start_date);
```

### Query Optimization

1. **Subquery for exclusion** instead of loading all assignments:
```python
assigned_subquery = (
    select(StudyAssignment.respondent_id)
    .where(StudyAssignment.study_id == study_id)
)
query = query.where(Respondent.id.not_in(assigned_subquery))
```

2. **Pagination** on all list endpoints to limit result sets

3. **Eager loading** for related data when needed:
```python
result = await db.execute(
    select(Study)
    .options(selectinload(Study.criteria))
    .where(Study.id == study_id)
)
```

### Diagnosing Slow Queries

```python
# Enable query logging
engine = create_async_engine(
    settings.database_url,
    echo=True,  # Logs all SQL queries
)
```

```sql
-- Use EXPLAIN ANALYZE for query analysis
EXPLAIN ANALYZE
SELECT * FROM respondents
WHERE state = 'NY' AND age BETWEEN 25 AND 45;
```

---

## Deployment & Migrations

### Alembic Migration Workflow

```bash
# Create a new migration
alembic revision -m "Add new_column to respondents"

# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Migration File Structure

```python
"""Create respondents table

Revision ID: 001
Revises:
Create Date: 2026-02-20
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None

def upgrade() -> None:
    op.create_table(
        'respondents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        # ... more columns
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_respondents_email', 'respondents', ['email'], unique=True)

def downgrade() -> None:
    op.drop_index('ix_respondents_email', table_name='respondents')
    op.drop_table('respondents')
```

### Production Deployment Checklist

1. **Test migration locally** against a copy of production data
2. **Backup database** before running migrations
3. **Run migrations** as part of deployment pipeline (before app restart)
4. **Monitor** for errors during migration
5. **Have rollback plan** ready (`alembic downgrade -1`)

### Risk Mitigation for Schema Changes

- **Adding columns**: Add as nullable first, backfill data, then add NOT NULL constraint
- **Adding indexes**: Use `CONCURRENTLY` to avoid table locks:
  ```sql
  CREATE INDEX CONCURRENTLY ix_new_index ON table(column);
  ```
- **Renaming columns**: Create new column, migrate data, drop old column (3-step process)

---

## Testing

### Running Tests

```bash
# Start test database
docker compose up -d db_test

# Run all tests
pytest -v

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_matching.py -v
```

### Test Configuration

```python
# tests/conftest.py
@pytest.fixture(scope="function")
async def db_session():
    """Create a fresh database for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

### Example Test

```python
@pytest.mark.asyncio
async def test_match_respondents_by_age(client: AsyncClient):
    """Test matching respondents by age range."""
    # Create respondents with different ages
    for age in [22, 30, 35, 50, 65]:
        await client.post("/api/respondents", json={
            "first_name": f"Age{age}",
            "last_name": "Test",
            "email": f"age{age}@example.com",
            "age": age,
        })

    # Create study with age criteria (25-45)
    study_response = await client.post("/api/studies", json={
        "title": "Age Match Test",
        "client_name": "Test",
        "methodology": "focus_group",
        "target_count": 10,
        "criteria": [
            {"field_name": "age", "operator": "between", "value": [25, 45]},
        ],
    })
    study_id = study_response.json()["id"]

    # Verify matching
    response = await client.get(f"/api/studies/{study_id}/match")
    assert response.json()["total"] == 2  # Ages 30 and 35
```

---

## Quick Reference

### Start Development Server
```bash
source venv/bin/activate
python -m uvicorn app.main:app --reload
```

### Seed Database
```bash
python -m scripts.seed_data
```

### API Documentation
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

### Sample API Calls
```bash
# List respondents
curl http://localhost:8001/api/respondents

# Create study
curl -X POST http://localhost:8001/api/studies \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Study","client_name":"Client","methodology":"idi","target_count":10}'

# Find matching respondents
curl http://localhost:8001/api/studies/1/match
```

---

## Contact

**Kent Lucky Buhawe**
Built as a technical demonstration for Recruit and Field interview process.
