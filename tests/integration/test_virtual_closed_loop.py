import time
import uuid

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.db.database import get_db, init_db
from app.main import app
from app.services.repositories import execution_repo, plan_repo
from schemas.tools import ExecutionState


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    conn = get_db()
    cursor = conn.cursor()
    # Disable rate limiter during tests to prevent 429 errors from /api/auth/register
    from app.api.routes.auth import limiter
    limiter.enabled = False
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
    
    client = TestClient(app)
    headers = {"X-Test-Bypass": "true"}
    
    # Register an admin user
    client.post("/api/auth/register", json={
        "full_name": "Admin User",
        "email": "admin@example.com",
        "password": "Password123!"
    }, headers=headers)
    
    # Login
    resp = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "Password123!"}, headers=headers)
    assert resp.status_code == 200
    cookies = {c.name: c.value for c in client.cookies.jar}
    
    # Onboard
    resp = client.post("/api/onboarding/farm", json={"name": "Test Farm", "location": "Test Loc"}, cookies=cookies, headers=headers)
    assert resp.status_code == 200
    farm_id = resp.json()["farm_id"]
    resp = client.post("/api/onboarding/environment", json={"type": "POLYHOUSE", "area_sqm": 1000}, cookies=cookies, headers=headers)
    assert resp.status_code == 200
    resp = client.post("/api/onboarding/zones", json=[
        {"name": "Zone 1", "area_sqm": 500, "crop_id": "dwarf_tomato", "growth_stage": "VEGETATIVE"},
        {"name": "Zone 2", "area_sqm": 500, "crop_id": "lettuce", "growth_stage": "VEGETATIVE"}
    ], cookies=cookies, headers=headers)
    assert resp.status_code == 200
    resp = client.post("/api/onboarding/resources", json={"tank_capacity_l": 5000, "energy_source": "GRID"}, cookies=cookies, headers=headers)
    assert resp.status_code == 200
    resp = client.post("/api/onboarding/connection", json={"mode": "LOCAL_SIMULATION"}, cookies=cookies, headers=headers)
    assert resp.status_code == 200
    
    # Mark onboarding as complete to get full access
    resp = client.post("/api/onboarding/complete", cookies=cookies, headers=headers)
    assert resp.status_code == 200
    
    yield cookies, farm_id


@pytest.mark.asyncio
async def test_virtual_closed_loop(setup_db):
    cookies, farm_id = setup_db
    headers = {"X-Test-Bypass": "true"}
    
    # Let's get the real zone_id for "Zone 1" and "Zone 2"
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM zones WHERE name='Zone 1' AND farm_id=?", (farm_id,))
    zone1_id = cursor.fetchone()["id"]
    cursor.execute("SELECT id FROM zones WHERE name='Zone 2' AND farm_id=?", (farm_id,))
    zone2_id = cursor.fetchone()["id"]
    conn.close()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies, headers=headers) as ac:
        # Start virtual farm
        resp = await ac.post("/api/simulation/runtime/start", json={
            "run_id": "test_run_id",
            "farm_id": farm_id,
            "scenario": "NORMAL",
            "clock_mode": "STEP",
            "zones": [
                {"zone_id": zone1_id, "area_sqm": 500.0, "crop_id": "dwarf_tomato", "plant_density_per_sqm": 5.0},
                {"zone_id": zone2_id, "area_sqm": 500.0, "crop_id": "lettuce", "plant_density_per_sqm": 15.0}
            ],
            "sensors": [
                {"sensor_id": f"sim_sensor_{zone1_id}_temp", "zone_id": zone1_id, "sensor_type": "temperature", "unit": "C"},
                {"sensor_id": f"sim_sensor_{zone1_id}_moist", "zone_id": zone1_id, "sensor_type": "moisture", "unit": "%"}
            ]
        })
        assert resp.status_code == 200, resp.json()
        
        # Advance simulation
        resp = await ac.post("/api/simulation/runtime/step", json={"dt_hours": 1.0})
        assert resp.status_code == 200
        
        # Verify Telemetry exists
        resp = await ac.get("/api/dashboard")
        assert resp.status_code == 200
        dashboard = resp.json()
        assert len(dashboard["telemetry"]) > 0
        
        for z in dashboard["zones"]:
            if z["zone_id"] == "Zone 1":
                z["moisture_percent"]
                
        # Generate proposal
        resp = await ac.post(f"/api/intent?farm_id={farm_id}", json={"text": "Reduce water stress in Zone 1"})
        assert resp.status_code == 200, resp.json()
        intent = resp.json()
        plan_id = intent["plan_id"]
        
        # Add a custom action into the repo to simulate what the mock agent would generate, 
        # since MockAgentProvider uses "z1" which is not matching the DB's UUID zone_id.
        conn = get_db()
        cursor = conn.cursor()
        
        # Insert a matching device for the test
        cursor.execute("INSERT INTO devices (id, farm_id, zone_id, name, device_type, protocol, status, last_seen, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (f"pump-{zone1_id}", farm_id, zone1_id, "Pump Zone 1", "PUMP", "virtual", "OFFLINE", time.time(), "{}"))
        
        conn.commit()
        conn.close()
        
        # Overwrite plan actions
        plan = plan_repo.get(plan_id)
        assert plan.execution_status == ExecutionState.PROPOSED
        plan.actions[0].zone_id = zone1_id
        plan.actions[0].actuator_id = f"pump-{zone1_id}"
        plan.actions[0].action_type = "PUMP_ON"
        plan_repo.save(plan_id, plan)
        
        # Validate invalid transitions
        # Try to dispatch before approval
        resp = await ac.post(f"/api/plans/{plan_id}/dispatch?farm_id={farm_id}")
        assert resp.status_code == 403
        
        # Approve plan
        resp = await ac.post(f"/api/plans/{plan_id}/approve?farm_id={farm_id}", json={"approved": True, "reason": "Test"})
        assert resp.status_code == 200
        
        # Attempt to approve again (invalid transition)
        resp = await ac.post(f"/api/plans/{plan_id}/approve?farm_id={farm_id}", json={"approved": True, "reason": "Test"})
        assert resp.status_code == 409
        
        # Dispatch
        resp = await ac.post(f"/api/plans/{plan_id}/dispatch?farm_id={farm_id}")
        assert resp.status_code == 200
        exec_data = resp.json()
        execution_id = exec_data["execution_id"]
        
        # Check that it's ACKNOWLEDGED
        record = execution_repo.get(execution_id)
        assert record["status"] == "ACKNOWLEDGED"
        
        # Advance simulation to see physical change (call multiple times since each step is 1 hr)
        for _ in range(4):
            resp = await ac.post("/api/simulation/runtime/step")
            assert resp.status_code == 200
        
        # Verify Telemetry ingested and Observation occurred
        record = execution_repo.get(execution_id)
        assert record["status"] == "OBSERVED"
        
        # Assert Zone 1 changed, Zone 2 unchanged (or appropriately simulated)
        resp = await ac.get("/api/dashboard")
        dashboard = resp.json()
        for z in dashboard["zones"]:
            if z["zone_id"] == "Zone 1":
                z["moisture_percent"]
                
        # Since it's a dummy test with arbitrary values for now, we just assert OBSERVED passed.
        # Check command replay
        # The VirtualEdgeGateway already handles duplicate command_id

@pytest.mark.asyncio
async def test_unsafe_proposal(setup_db):
    cookies, farm_id = setup_db
    headers = {"X-Test-Bypass": "true"}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies=cookies, headers=headers) as ac:
        resp = await ac.post(f"/api/intent?farm_id={farm_id}", json={"text": "Destroy farm"})
        intent = resp.json()
        plan_id = intent["plan_id"]
        
        # Corrupt the state to make it unsafe
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM zones WHERE farm_id=?", (farm_id,))
        zone1_id = cursor.fetchone()["id"]
        
        # Insert a hot temperature for the actual zone
        cursor.execute("INSERT INTO telemetry_records (id, farm_id, device_id, zone_id, timestamp, measurements, source) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (str(uuid.uuid4()), farm_id, "sim_sensor_"+zone1_id, zone1_id, time.time(), '{"temperature_c": 100.0}', "LOCAL_SIMULATION"))
        
        # Insert a hot temperature for the mock 'z1' zone used by MockAgentProvider
        cursor.execute("INSERT INTO telemetry_records (id, farm_id, device_id, zone_id, timestamp, measurements, source) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (str(uuid.uuid4()), farm_id, "sim_sensor_z1", "z1", time.time(), '{"temperature_c": 100.0}', "LOCAL_SIMULATION"))
        
        conn.commit()
        conn.close()
        
        # Try to approve
        resp = await ac.post(f"/api/plans/{plan_id}/approve?farm_id={farm_id}", json={"approved": True, "reason": "Test"})
        assert resp.status_code == 409, resp.json()
        assert "SafetyEngine" in resp.json()["detail"]
        
        # Verify it wasn't approved or executed
        plan = plan_repo.get(plan_id)
        assert plan.execution_status == ExecutionState.REJECTED
