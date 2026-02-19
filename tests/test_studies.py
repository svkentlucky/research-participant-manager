import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_study(client: AsyncClient):
    """Test creating a new study with criteria."""
    response = await client.post(
        "/api/studies",
        json={
            "title": "Coffee Drinking Habits",
            "client_name": "Starbucks",
            "methodology": "focus_group",
            "target_count": 12,
            "incentive_amount": "150.00",
            "criteria": [
                {"field_name": "age", "operator": "between", "value": [25, 45]},
                {"field_name": "state", "operator": "in", "value": ["NY", "CA", "TX"]},
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Coffee Drinking Habits"
    assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_list_studies(client: AsyncClient):
    """Test listing studies with filters."""
    # Create studies
    for i, status in enumerate(["draft", "recruiting", "completed"]):
        await client.post(
            "/api/studies",
            json={
                "title": f"Study {i}",
                "client_name": "Test Client",
                "methodology": "idi",
                "target_count": 10,
                "status": status,
            },
        )

    # List all
    response = await client.get("/api/studies")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3

    # Filter by status
    response = await client.get("/api/studies?status=recruiting")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_get_study_detail(client: AsyncClient):
    """Test getting study details with criteria and counts."""
    # Create study with criteria
    create_response = await client.post(
        "/api/studies",
        json={
            "title": "Detail Test",
            "client_name": "Test Co",
            "methodology": "survey",
            "target_count": 50,
            "criteria": [
                {"field_name": "household_income", "operator": "in", "value": ["75k-100k", "100k+"]},
            ],
        },
    )
    study_id = create_response.json()["id"]

    # Get detail
    response = await client.get(f"/api/studies/{study_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Detail Test"
    assert len(data["criteria"]) == 1
    assert data["criteria"][0]["field_name"] == "household_income"
    assert "assignment_counts" in data


@pytest.mark.asyncio
async def test_update_study(client: AsyncClient):
    """Test updating a study."""
    # Create study
    create_response = await client.post(
        "/api/studies",
        json={
            "title": "Update Me",
            "client_name": "Client",
            "methodology": "ethnography",
            "target_count": 8,
        },
    )
    study_id = create_response.json()["id"]

    # Update
    response = await client.put(
        f"/api/studies/{study_id}",
        json={
            "status": "recruiting",
            "target_count": 10,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "recruiting"
    assert data["target_count"] == 10


@pytest.mark.asyncio
async def test_assign_respondents(client: AsyncClient):
    """Test assigning respondents to a study."""
    # Create study
    study_response = await client.post(
        "/api/studies",
        json={
            "title": "Assignment Test",
            "client_name": "Client",
            "methodology": "idi",
            "target_count": 5,
        },
    )
    study_id = study_response.json()["id"]

    # Create respondents
    respondent_ids = []
    for i in range(2):
        resp = await client.post(
            "/api/respondents",
            json={
                "first_name": f"Assign{i}",
                "last_name": "Test",
                "email": f"assign{i}@example.com",
            },
        )
        respondent_ids.append(resp.json()["id"])

    # Assign
    response = await client.post(
        f"/api/studies/{study_id}/assign",
        json={"respondent_ids": respondent_ids},
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 2
    assert all(a["status"] == "invited" for a in data)
