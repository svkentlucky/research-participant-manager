import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_respondent(client: AsyncClient):
    """Test creating a new respondent."""
    response = await client.post(
        "/api/respondents",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "555-1234",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "age": 35,
            "gender": "male",
            "household_income": "75k-100k",
            "occupation": "Software Engineer",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert data["email"] == "john.doe@example.com"
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_create_respondent_duplicate_email(client: AsyncClient):
    """Test that duplicate emails are rejected."""
    respondent_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "duplicate@example.com",
    }

    response = await client.post("/api/respondents", json=respondent_data)
    assert response.status_code == 201

    response = await client.post("/api/respondents", json=respondent_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_respondents(client: AsyncClient):
    """Test listing respondents with pagination."""
    # Create some respondents
    for i in range(3):
        await client.post(
            "/api/respondents",
            json={
                "first_name": f"User{i}",
                "last_name": "Test",
                "email": f"user{i}@example.com",
                "state": "NY" if i < 2 else "CA",
                "age": 25 + i,
            },
        )

    # List all
    response = await client.get("/api/respondents")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3

    # Filter by state
    response = await client.get("/api/respondents?state=NY")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_get_respondent(client: AsyncClient):
    """Test getting a single respondent."""
    # Create respondent
    create_response = await client.post(
        "/api/respondents",
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
        },
    )
    respondent_id = create_response.json()["id"]

    # Get respondent
    response = await client.get(f"/api/respondents/{respondent_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Jane"


@pytest.mark.asyncio
async def test_get_respondent_not_found(client: AsyncClient):
    """Test getting a non-existent respondent."""
    response = await client.get("/api/respondents/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_respondent(client: AsyncClient):
    """Test updating a respondent."""
    # Create respondent
    create_response = await client.post(
        "/api/respondents",
        json={
            "first_name": "Update",
            "last_name": "Me",
            "email": "update@example.com",
            "age": 30,
        },
    )
    respondent_id = create_response.json()["id"]

    # Update respondent
    response = await client.put(
        f"/api/respondents/{respondent_id}",
        json={"age": 31, "city": "Boston"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["age"] == 31
    assert data["city"] == "Boston"


@pytest.mark.asyncio
async def test_delete_respondent(client: AsyncClient):
    """Test soft deleting a respondent."""
    # Create respondent
    create_response = await client.post(
        "/api/respondents",
        json={
            "first_name": "Delete",
            "last_name": "Me",
            "email": "delete@example.com",
        },
    )
    respondent_id = create_response.json()["id"]

    # Delete respondent
    response = await client.delete(f"/api/respondents/{respondent_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False
