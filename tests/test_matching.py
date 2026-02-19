import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_match_respondents_by_age(client: AsyncClient):
    """Test matching respondents by age range."""
    # Create respondents with different ages
    ages = [22, 30, 35, 50, 65]
    for i, age in enumerate(ages):
        await client.post(
            "/api/respondents",
            json={
                "first_name": f"Age{age}",
                "last_name": "Test",
                "email": f"age{age}@example.com",
                "age": age,
            },
        )

    # Create study with age criteria (25-45)
    study_response = await client.post(
        "/api/studies",
        json={
            "title": "Age Match Test",
            "client_name": "Test",
            "methodology": "focus_group",
            "target_count": 10,
            "criteria": [
                {"field_name": "age", "operator": "between", "value": [25, 45]},
            ],
        },
    )
    study_id = study_response.json()["id"]

    # Match
    response = await client.get(f"/api/studies/{study_id}/match")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2  # Ages 30 and 35
    ages_found = [r["age"] for r in data["items"]]
    assert 30 in ages_found
    assert 35 in ages_found


@pytest.mark.asyncio
async def test_match_respondents_by_state(client: AsyncClient):
    """Test matching respondents by state."""
    # Create respondents in different states
    states = ["NY", "CA", "TX", "FL", "WA"]
    for i, state in enumerate(states):
        await client.post(
            "/api/respondents",
            json={
                "first_name": f"State{state}",
                "last_name": "Test",
                "email": f"state{state}@example.com",
                "state": state,
            },
        )

    # Create study targeting NY and CA
    study_response = await client.post(
        "/api/studies",
        json={
            "title": "State Match Test",
            "client_name": "Test",
            "methodology": "idi",
            "target_count": 5,
            "criteria": [
                {"field_name": "state", "operator": "in", "value": ["NY", "CA"]},
            ],
        },
    )
    study_id = study_response.json()["id"]

    # Match
    response = await client.get(f"/api/studies/{study_id}/match")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    states_found = [r["state"] for r in data["items"]]
    assert "NY" in states_found
    assert "CA" in states_found


@pytest.mark.asyncio
async def test_match_excludes_assigned(client: AsyncClient):
    """Test that matching excludes already assigned respondents."""
    # Create respondents
    respondent_ids = []
    for i in range(3):
        resp = await client.post(
            "/api/respondents",
            json={
                "first_name": f"Exclude{i}",
                "last_name": "Test",
                "email": f"exclude{i}@example.com",
                "state": "NY",
            },
        )
        respondent_ids.append(resp.json()["id"])

    # Create study targeting NY
    study_response = await client.post(
        "/api/studies",
        json={
            "title": "Exclude Test",
            "client_name": "Test",
            "methodology": "survey",
            "target_count": 5,
            "criteria": [
                {"field_name": "state", "operator": "eq", "value": "NY"},
            ],
        },
    )
    study_id = study_response.json()["id"]

    # Match before assignment
    response = await client.get(f"/api/studies/{study_id}/match")
    assert response.json()["total"] == 3

    # Assign one respondent
    await client.post(
        f"/api/studies/{study_id}/assign",
        json={"respondent_ids": [respondent_ids[0]]},
    )

    # Match after assignment (should exclude assigned)
    response = await client.get(f"/api/studies/{study_id}/match")
    assert response.json()["total"] == 2

    # Match with exclude_assigned=false
    response = await client.get(f"/api/studies/{study_id}/match?exclude_assigned=false")
    assert response.json()["total"] == 3


@pytest.mark.asyncio
async def test_match_multiple_criteria(client: AsyncClient):
    """Test matching with multiple criteria (AND logic)."""
    # Create diverse respondents
    respondents_data = [
        {"age": 30, "state": "NY", "household_income": "75k-100k"},
        {"age": 30, "state": "CA", "household_income": "75k-100k"},
        {"age": 50, "state": "NY", "household_income": "75k-100k"},
        {"age": 30, "state": "NY", "household_income": "25k-50k"},
    ]
    for i, data in enumerate(respondents_data):
        await client.post(
            "/api/respondents",
            json={
                "first_name": f"Multi{i}",
                "last_name": "Test",
                "email": f"multi{i}@example.com",
                **data,
            },
        )

    # Create study with multiple criteria
    study_response = await client.post(
        "/api/studies",
        json={
            "title": "Multi Criteria Test",
            "client_name": "Test",
            "methodology": "focus_group",
            "target_count": 10,
            "criteria": [
                {"field_name": "age", "operator": "between", "value": [25, 40]},
                {"field_name": "state", "operator": "eq", "value": "NY"},
                {"field_name": "household_income", "operator": "in", "value": ["75k-100k", "100k+"]},
            ],
        },
    )
    study_id = study_response.json()["id"]

    # Match - only first respondent meets all criteria
    response = await client.get(f"/api/studies/{study_id}/match")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["age"] == 30
    assert data["items"][0]["state"] == "NY"
    assert data["items"][0]["household_income"] == "75k-100k"
