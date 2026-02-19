# Research Participant Manager API

A production-ready **FastAPI + PostgreSQL** REST API for managing qualitative research respondents, studies, and participant matching. Built as a technical demonstration showcasing backend development skills.

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Async Python web framework |
| **PostgreSQL 16** | Relational database with JSONB |
| **SQLAlchemy 2.0** | Async ORM with type hints |
| **Alembic** | Database migrations |
| **Pydantic v2** | Data validation |
| **pytest** | Async testing |

## Quick Start

```bash
# 1. Start PostgreSQL
docker compose up -d

# 2. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Run migrations
alembic upgrade head

# 4. Seed sample data (150 respondents, 12 studies)
python -m scripts.seed_data

# 5. Start server
python -m uvicorn app.main:app --reload --port 8001
```

**API Docs:** http://localhost:8001/docs

## Key Features

### 1. Smart Matching Engine

Match respondents to studies based on flexible JSONB criteria:

```bash
# Find respondents matching study criteria
curl http://localhost:8001/api/studies/5/match
```

**Response:**
```json
{
  "items": [
    {"id": 25, "first_name": "Katherine", "age": 69, "household_income": "150k+", ...}
  ],
  "total": 26,
  "study_id": 5
}
```

### 2. Flexible Screener Criteria

```json
{
  "criteria": [
    {"field_name": "age", "operator": "between", "value": [25, 45]},
    {"field_name": "state", "operator": "in", "value": ["NY", "CA", "TX"]},
    {"field_name": "household_income", "operator": "gte", "value": "75k-100k"}
  ]
}
```

**Supported operators:** `eq`, `neq`, `gte`, `lte`, `in`, `between`

### 3. Assignment Tracking

Track participants through the research lifecycle:
`invited` → `confirmed` → `completed` (or `no_show` / `rejected`)

## API Endpoints

### Respondents
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/respondents` | Create respondent |
| GET | `/api/respondents` | List with filters + pagination |
| GET | `/api/respondents/{id}` | Get single respondent |
| PUT | `/api/respondents/{id}` | Update |
| DELETE | `/api/respondents/{id}` | Soft delete |

### Studies
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/studies` | Create with screener criteria |
| GET | `/api/studies` | List studies |
| GET | `/api/studies/{id}` | Get with criteria & counts |
| GET | `/api/studies/{id}/match` | **Find matching respondents** |
| POST | `/api/studies/{id}/assign` | Assign respondents |

### Assignments
| Method | Endpoint | Description |
|--------|----------|-------------|
| PATCH | `/api/assignments/{id}` | Update status |

## Sample API Calls

```bash
# Create a respondent
curl -X POST http://localhost:8001/api/respondents \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Jane","last_name":"Smith","email":"jane@example.com","state":"NY","age":32,"household_income":"100k-150k"}'

# Create a study with criteria
curl -X POST http://localhost:8001/api/studies \
  -H "Content-Type: application/json" \
  -d '{"title":"Coffee Habits","client_name":"Starbucks","methodology":"focus_group","target_count":12,"criteria":[{"field_name":"age","operator":"between","value":[25,45]}]}'

# Find matching respondents
curl "http://localhost:8001/api/studies/1/match"

# Assign respondents to study
curl -X POST http://localhost:8001/api/studies/1/assign \
  -H "Content-Type: application/json" \
  -d '{"respondent_ids":[1,2,3]}'

# Confirm assignment
curl -X PATCH http://localhost:8001/api/assignments/1 \
  -H "Content-Type: application/json" \
  -d '{"status":"confirmed"}'
```

## Database Schema

```
respondents          studies              screener_criteria
├── id (PK)          ├── id (PK)          ├── id (PK)
├── first_name       ├── title            ├── study_id (FK)
├── last_name        ├── client_name      ├── field_name
├── email (UNIQUE)   ├── methodology      ├── operator
├── state            ├── target_count     └── value (JSONB)
├── age              ├── status
├── household_income └── incentive_amount
└── is_active
                     study_assignments
                     ├── id (PK)
                     ├── study_id (FK)
                     ├── respondent_id (FK)
                     ├── status
                     └── UNIQUE(study_id, respondent_id)
```

## Project Structure

```
app/
├── main.py              # FastAPI app
├── config.py            # Environment settings
├── database.py          # Async DB sessions
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic validation
├── routers/             # API endpoints
└── services/            # Business logic (matching engine)

alembic/versions/        # Migrations (one per table)
scripts/seed_data.py     # Sample data generator
tests/                   # pytest async tests
```

## Running Tests

```bash
docker compose up -d db_test
pytest -v
```

## Documentation

See [DOCUMENTATION.md](DOCUMENTATION.md) for detailed technical documentation including:
- SQL query examples with JOINs and aggregations
- Index strategy and performance optimization
- Migration workflow and production deployment
- Code architecture and design patterns

---

**Author:** Kent Lucky Buhawe
**Purpose:** Technical demonstration for Recruit and Field
