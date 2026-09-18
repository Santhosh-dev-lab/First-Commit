from fastapi.testclient import TestClient

from app.api.deps import get_authorized_farm
from app.main import app
from app.services.auth_service import UserInfo, get_current_user
from app.services.repositories import plan_repo
from schemas.tools import ControlPlanProposal, ExecutionState

client = TestClient(app)
client.cookies["csrf_token"] = "test_csrf"
client.headers["X-CSRF-Token"] = "test_csrf"

def mock_get_current_user():
    return UserInfo(id="test_user", full_name="Test User", email="test@test.com", role="OWNER")

def mock_get_authorized_farm():
    return {"farm": {"id": "test_farm"}}

import pytest

@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_authorized_farm] = mock_get_authorized_farm
    yield
    app.dependency_overrides.clear()

def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"



def test_simulate() -> None:
    req = {
        "scenario_name": "test_sim",
        "days": 1,
        "dt_hours": 1.0,
        "zone_ids": ["zone_1"]
    }
    response = client.post("/api/simulate", json=req)
    assert response.status_code == 200
    data = response.json()
    assert data["total_days_simulated"] == 1.0

def test_intent() -> None:
    req = {
        "text": "Decrease water by 10%",
        "zone_id": "zone_1"
    }
    response = client.post("/api/intent", json=req)
    assert response.status_code == 200
    data = response.json()
    assert "plan_id" in data

def test_execution_authorization_flow() -> None:
    # Setup mock plan
    plan_id = "test_plan_1"
    plan = ControlPlanProposal(farm_id="test_farm", actions=[], execution_status=ExecutionState.PROPOSED, created_by="test")
    plan_repo.save(plan_id, plan)
    
    # 1. Attempt dispatch before approval -> Expect 403 Forbidden
    response = client.post(f"/api/plans/{plan_id}/dispatch")
    assert response.status_code == 403
    
    # Verify state didn't change
    plan_opt = plan_repo.get(plan_id)
    assert plan_opt is not None
    assert plan_opt.execution_status == ExecutionState.PROPOSED

    # 2. Approve plan
    approval_req = {"approved": True, "reason": "Looks good"}
    response = client.post(f"/api/plans/{plan_id}/approve", json=approval_req)
    assert response.status_code == 200
    
    # Verify state changed
    plan_opt = plan_repo.get(plan_id)
    assert plan_opt is not None
    assert plan_opt.execution_status == ExecutionState.APPROVED
    
    # 3. Dispatch approved plan
    response = client.post(f"/api/plans/{plan_id}/dispatch")
    assert response.status_code == 200
    
    # Verify state changed
    plan_opt = plan_repo.get(plan_id)
    assert plan_opt is not None
    assert plan_opt.execution_status == ExecutionState.DISPATCHED
