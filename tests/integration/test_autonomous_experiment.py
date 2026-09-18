import time

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.db.database import get_db, init_db
from app.main import app
from app.services.experiment_service import experiment_repo


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM virtual_farm_runs")
    cursor.execute("DELETE FROM command_execution_log")
    cursor.execute("DELETE FROM telemetry_records")
    cursor.execute("DELETE FROM actuators")
    cursor.execute("DELETE FROM sensors")
    cursor.execute("DELETE FROM devices")
    cursor.execute("DELETE FROM farm_connections")
    cursor.execute("DELETE FROM resources")
    cursor.execute("DELETE FROM zones")
    cursor.execute("DELETE FROM farms")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM sessions")
    conn.commit()
    conn.close()
    
    # Also clear the in-memory experiment repo
    experiment_repo._experiments.clear()
    
    client = TestClient(app)
    # Register an admin user
    client.post("/api/auth/register", json={
        "full_name": "Admin User",
        "email": "admin@example.com",
        "password": "Password123!"
    })
    
    headers = {"X-Test-Bypass": "true"}
    
    # Login
    resp = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "Password123!"}, headers=headers)
    assert resp.status_code == 200
    cookies = {c.name: c.value for c in client.cookies.jar}
    
    resp = client.post("/api/onboarding/farm", json={"name": "Test Farm", "location": "Test Loc"}, cookies=cookies, headers=headers)
    farm_id = resp.json()["farm_id"]
    resp = client.post("/api/onboarding/environment", json={"type": "POLYHOUSE", "area_sqm": 1000}, cookies=cookies, headers=headers)
    assert resp.status_code == 200, resp.json()
    resp = client.post("/api/onboarding/zones", json=[
        {"name": "Zone 1", "area_sqm": 500, "crop_id": "dwarf_tomato", "growth_stage": "VEGETATIVE"},
        {"name": "Zone 2", "area_sqm": 500, "crop_id": "lettuce", "growth_stage": "VEGETATIVE"}
    ], cookies=cookies, headers=headers)
    assert resp.status_code == 200, resp.json()
    resp = client.post("/api/onboarding/resources", json={"tank_capacity_l": 5000, "energy_source": "GRID"}, cookies=cookies, headers=headers)
    assert resp.status_code == 200, resp.json()
    resp = client.post("/api/onboarding/connection", json={"mode": "LOCAL_SIMULATION"}, cookies=cookies, headers=headers)
    assert resp.status_code == 200, resp.json()
    resp = client.post("/api/onboarding/complete", cookies=cookies, headers=headers)
    assert resp.status_code == 200, resp.json()
    
    
    # Insert required devices for BaselineController
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM zones WHERE farm_id=?", (farm_id,))
    for row in cursor.fetchall():
        z_id = row["id"]
        now = time.time()
        for dev_type, dev_name in [("PUMP", "pump"), ("VENT", "fan"), ("VENT", "heater"), ("VENT", "fogger"), ("VENT", "vent")]:
            cursor.execute(
                "INSERT INTO devices (id, farm_id, zone_id, name, device_type, protocol, status, last_seen, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (f"{dev_name}-{z_id}", farm_id, z_id, f"{dev_name} {z_id}", dev_type, "virtual", "OFFLINE", now, "{}")
            )
    conn.commit()
    conn.close()
    
    yield cookies, farm_id


@pytest.mark.asyncio
async def test_water_shortage_demonstration(setup_db):
    cookies, _farm_id = setup_db
    headers = {"X-Test-Bypass": "true"}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies, headers=headers) as ac:
        # Run experiment evaluating water minimization
        resp = await ac.post("/api/experiments", json={
            "objective": "WATER_MINIMIZATION",
            "weights": {
                "water_weight": 1.0,
                "stress_weight": 0.5,
                "energy_weight": 0.1,
                "yield_weight": 0.2
            },
            "scenario": "WATER_SHORTAGE",
            "seed": 42,
            "days": 7
        })
        
        assert resp.status_code == 200, resp.json()
        experiment = resp.json()
        
        experiment_id = experiment["experiment_id"]
        
        # Verify baseline exists
        assert experiment["baseline"] is not None
        
        # Verify candidates exist
        assert len(experiment["candidates"]) > 1
        
        # Determine winning candidate
        selected_id = experiment["selected_candidate_id"]
        assert selected_id is not None
        
        selected_candidate = next(c for c in experiment["candidates"] if c["candidate_id"] == selected_id)
        assert selected_candidate["status"] == "SAFE"
        
        # Ensure that selected candidate has less water than baseline
        assert selected_candidate["metrics"]["water_used_l"] <= experiment["baseline"]["metrics"]["water_used_l"]
        
        # Execute the selected strategy
        resp = await ac.post(f"/api/experiments/{experiment_id}/execute")
        assert resp.status_code == 200, resp.json()
        execution = resp.json()
        assert execution["status"] == "SUCCESS"
        assert execution["plan_id"] is not None

@pytest.mark.asyncio
async def test_reproducibility(setup_db):
    cookies, _farm_id = setup_db
    headers = {"X-Test-Bypass": "true"}
    
    payload = {
        "objective": "WATER_MINIMIZATION",
        "weights": {
            "water_weight": 1.0,
            "stress_weight": 0.5,
            "energy_weight": 0.1,
            "yield_weight": 0.2
        },
        "scenario": "WATER_SHORTAGE",
        "seed": 100,
        "days": 2
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies, headers=headers) as ac:
        resp1 = await ac.post("/api/experiments", json=payload)
        exp1 = resp1.json()
        
        resp2 = await ac.post("/api/experiments", json=payload)
        exp2 = resp2.json()
        
        assert exp1["selected_strategy"]["policy_id"] == exp2["selected_strategy"]["policy_id"]
        
        for c1, c2 in zip(exp1["candidates"], exp2["candidates"]):
            assert c1["score"] == c2["score"]
            assert c1["metrics"]["water_used_l"] == c2["metrics"]["water_used_l"]

@pytest.mark.asyncio
async def test_unsafe_rejection(setup_db):
    cookies, _farm_id = setup_db
    headers = {"X-Test-Bypass": "true"}
    
    # If a strategy reduces water so much that crop stress hits limits or temperatures spike (scenario extreme)
    # The simulation should flag a violation.
    # We will trigger this by creating a custom objective or using an extreme scenario.
    payload = {
        "objective": "WATER_MINIMIZATION",
        "weights": {
            "water_weight": 10.0,
            "stress_weight": 0.0, # Ignore stress
            "energy_weight": 0.0,
            "yield_weight": 0.0
        },
        "scenario": "EXTREME_HEAT",
        "seed": 42,
        "days": 15
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies, headers=headers) as ac:
        resp = await ac.post("/api/experiments", json=payload)
        assert resp.status_code == 200, resp.json()
        exp = resp.json()
        
        # Verify all candidates are REJECTED
        import json
        print(json.dumps(exp, indent=2))
        assert all(c["status"] == "REJECTED" for c in exp["candidates"])
        
        # Ensure NO selected candidate
        assert exp["selected_candidate_id"] is None
        assert exp["selected_strategy"] is None

@pytest.mark.asyncio
async def test_execute_experiment(setup_db):
    cookies, _farm_id = setup_db
    headers = {"X-Test-Bypass": "true"}
    
    payload = {
        "objective": "WATER_MINIMIZATION",
        "weights": {
            "water_weight": 10.0,
            "stress_weight": 0.0,
            "energy_weight": 0.0,
            "yield_weight": 0.0
        },
        "scenario": "NORMAL",
        "seed": 42,
        "days": 15
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies, headers=headers) as ac:
        resp = await ac.post("/api/experiments", json=payload)
        assert resp.status_code == 200, resp.json()
        exp_id = resp.json()["experiment_id"]
        
        # Execute the selected strategy
        resp = await ac.post(f"/api/experiments/{exp_id}/execute")
        assert resp.status_code == 200, resp.json()
        
        result = resp.json()
        assert result["status"] == "SUCCESS"
        assert "plan_id" in result
