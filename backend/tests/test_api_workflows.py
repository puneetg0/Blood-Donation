import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-only-secret-key"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.session import Base, get_db
from app.main import app
from app.models.enums import Role
from app.models.user import User

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def register(client, email, role="requester"):
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Test Person",
            "email": email,
            "password": "test-password-123",
            "role": role,
        },
    )
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_admin():
    db = TestSession()
    admin = User(
        full_name="Administrator",
        email="admin@example.test",
        password_hash=hash_password("admin-password-123"),
        role=Role.admin,
    )
    db.add(admin)
    db.commit()
    db.close()


def test_registration_validates_input_and_rejects_admin_role(client):
    assert client.get("/api/auth/me").status_code == 401

    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Admin",
            "email": "admin@example.test",
            "password": "test-password-123",
            "role": "admin",
        },
    )
    assert response.status_code == 422

    long_password = "é" * 37
    too_long_password = client.post(
        "/api/auth/register",
        json={
            "full_name": "Test Person",
            "email": "long@example.test",
            "password": long_password,
            "role": "requester",
        },
    )
    assert too_long_password.status_code == 422

    register(client, "duplicate@example.test")
    duplicate_email = client.post(
        "/api/auth/register",
        json={
            "full_name": "Duplicate User",
            "email": "DUPLICATE@example.test",
            "password": "test-password-123",
            "role": "requester",
        },
    )
    assert duplicate_email.status_code == 409

    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "   ",
            "email": "not-an-email",
            "password": "short",
            "role": "requester",
        },
    )
    assert response.status_code == 422


def test_donor_search_respects_consent_and_hides_contact_details(client):
    donor_headers = register(client, "donor@example.test", "donor")
    requester_headers = register(client, "requester@example.test")

    created = client.post(
        "/api/donors/",
        headers=donor_headers,
        json={
            "blood_group": "O+",
            "phone_number": "+1 (555) 123-4567",
            "city": "Springfield",
            "availability_status": "available",
            "consent_to_contact": True,
        },
    )
    assert created.status_code == 201, created.text
    donor_id = created.json()["id"]

    search = client.get(
        "/api/donors/",
        headers=requester_headers,
        params={"blood_group": "O+", "city": "field"},
    )
    assert search.status_code == 200
    assert search.json() == [
        {
            "id": donor_id,
            "blood_group": "O+",
            "city": "Springfield",
            "availability_status": "available",
        }
    ]

    private_profile = client.get(f"/api/donors/{donor_id}", headers=requester_headers)
    assert private_profile.status_code == 403
    owner_profile = client.get("/api/donors/me", headers=donor_headers)
    assert owner_profile.status_code == 200
    assert owner_profile.json()["phone_number"] == "+1 (555) 123-4567"

    opted_out = client.post(
        "/api/donors/",
        headers=register(client, "donor2@example.test", "donor"),
        json={
            "blood_group": "O+",
            "phone_number": "5551234567",
            "city": "Springfield",
            "availability_status": "available",
            "consent_to_contact": False,
        },
    )
    assert opted_out.status_code == 201
    results = client.get("/api/donors/", headers=requester_headers)
    assert len(results.json()) == 1


def test_requests_are_scoped_and_status_changes_are_audited(client):
    owner_headers = register(client, "owner@example.test")
    another_user_headers = register(client, "another@example.test")
    donor_headers = register(client, "donor@example.test", "donor")

    request = client.post(
        "/api/requests/",
        headers=owner_headers,
        json={
            "blood_group": "A+",
            "units_required": 2,
            "hospital_name": "Central Hospital",
            "city": "Springfield",
            "urgency": "urgent",
        },
    )
    assert request.status_code == 201, request.text
    request_id = request.json()["id"]

    assert client.get("/api/requests/", headers=another_user_headers).json() == []
    assert len(client.get("/api/requests/", headers=donor_headers).json()) == 1
    private_request = client.get(
        f"/api/requests/{request_id}", headers=another_user_headers
    )
    assert private_request.status_code == 403

    forbidden_advance = client.patch(
        f"/api/requests/{request_id}",
        headers=owner_headers,
        json={"status": "in_progress"},
    )
    assert forbidden_advance.status_code == 403

    cancelled = client.patch(
        f"/api/requests/{request_id}",
        headers=owner_headers,
        json={"status": "cancelled"},
    )
    assert cancelled.status_code == 200
    history = client.get(f"/api/requests/{request_id}/history", headers=owner_headers)
    assert history.status_code == 200
    assert history.json()[0]["previous_status"] == "pending"
    assert history.json()[0]["new_status"] == "cancelled"

    forbidden_history = client.get(
        f"/api/requests/{request_id}/history", headers=another_user_headers
    )
    assert forbidden_history.status_code == 403
    invalid_transition = client.patch(
        f"/api/requests/{request_id}",
        headers=owner_headers,
        json={"status": "pending"},
    )
    assert invalid_transition.status_code == 409


def test_admin_dashboard_is_role_protected(client):
    requester_headers = register(client, "requester@example.test")
    assert client.get("/api/admin/dashboard", headers=requester_headers).status_code == 403

    request = client.post(
        "/api/requests/",
        headers=requester_headers,
        json={
            "blood_group": "O-",
            "units_required": 1,
            "hospital_name": "City Hospital",
            "city": "Springfield",
        },
    )
    assert request.status_code == 201

    create_admin()
    admin_login = client.post(
        "/api/auth/login",
        json={"email": "admin@example.test", "password": "admin-password-123"},
    )
    assert admin_login.status_code == 200
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
    request_id = request.json()["id"]
    started = client.patch(
        f"/api/requests/{request_id}",
        headers=admin_headers,
        json={"status": "in_progress"},
    )
    assert started.status_code == 200
    fulfilled = client.patch(
        f"/api/requests/{request_id}",
        headers=admin_headers,
        json={"status": "fulfilled"},
    )
    assert fulfilled.status_code == 200

    dashboard = client.get("/api/admin/dashboard", headers=admin_headers)
    assert dashboard.status_code == 200
    assert dashboard.json() == {
        "total_donors": 0,
        "total_requests": 1,
        "pending_requests": 0,
        "in_progress_requests": 0,
        "fulfilled_requests": 1,
        "cancelled_requests": 0,
    }
    history = client.get(
        f"/api/requests/{request_id}/history", headers=admin_headers
    )
    assert [change["new_status"] for change in history.json()] == [
        "in_progress",
        "fulfilled",
    ]


def test_coordinations_require_request_owner_and_donor_consent(client):
    donor_headers = register(client, "donor@example.test", "donor")
    owner_headers = register(client, "owner@example.test")
    other_headers = register(client, "other@example.test")

    donor = client.post(
        "/api/donors/",
        headers=donor_headers,
        json={
            "blood_group": "B+",
            "phone_number": "5551234567",
            "city": "Springfield",
            "availability_status": "available",
            "consent_to_contact": True,
        },
    ).json()
    request = client.post(
        "/api/requests/",
        headers=owner_headers,
        json={
            "blood_group": "B+",
            "units_required": 1,
            "hospital_name": "Central Hospital",
            "city": "Springfield",
        },
    ).json()
    body = {"request_id": request["id"], "donor_id": donor["id"]}

    assert client.post("/api/coordinations/", headers=other_headers, json=body).status_code == 403
    assert client.post("/api/coordinations/", headers=owner_headers, json=body).status_code == 403

    create_admin()
    login = client.post(
        "/api/auth/login",
        json={"email": "admin@example.test", "password": "admin-password-123"},
    )
    admin_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    created = client.post("/api/coordinations/", headers=admin_headers, json=body)
    assert created.status_code == 201
    assert client.post("/api/coordinations/", headers=admin_headers, json=body).status_code == 409
    coordination_id = created.json()["id"]
    invalid_transition = client.patch(
        f"/api/coordinations/{coordination_id}",
        headers=admin_headers,
        json={"coordination_status": "completed"},
    )
    assert invalid_transition.status_code == 409
    contacted = client.patch(
        f"/api/coordinations/{coordination_id}",
        headers=admin_headers,
        json={"coordination_status": "contacted"},
    )

def test_donor_can_respond_to_coordination(client):
    donor_headers = register(client, "donor@example.test", "donor")
    owner_headers = register(client, "owner@example.test")

    donor = client.post(
        "/api/donors/",
        headers=donor_headers,
        json={
            "blood_group": "B+",
            "phone_number": "5551234567",
            "city": "Springfield",
            "availability_status": "available",
            "consent_to_contact": True,
        },
    ).json()
    request = client.post(
        "/api/requests/",
        headers=owner_headers,
        json={
            "blood_group": "B+",
            "units_required": 1,
            "hospital_name": "Central Hospital",
            "city": "Springfield",
        },
    ).json()
    body = {"request_id": request["id"], "donor_id": donor["id"]}

    create_admin()
    login = client.post(
        "/api/auth/login", json={"email": "admin@example.test", "password": "admin-password-123"}
    )
    admin_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    coord_response = client.post("/api/coordinations/", headers=admin_headers, json=body)
    assert coord_response.status_code == 201

    # Donor ACC EPTS a pending coordination
    coordination_id = coord_response.json()["id"]
    response = client.post(
        f"/api/coordinations/{coordination_id}/respond?response_text=accept",
        headers=donor_headers,
    )
    assert response.status_code == 200
    assert response.json()["coordination_status"] == "contacted"
    assert response.json()["donor_id"] == donor["id"]

    # Donor can decline a separate pending coordination
    decline_request = client.post(
        "/api/requests/",
        headers=owner_headers,
        json={
            "blood_group": "O+",
            "units_required": 1,
            "hospital_name": "Decline Hospital",
            "city": "Springfield",
        },
    ).json()
    decline_body = {"request_id": decline_request["id"], "donor_id": donor["id"]}
    decline_coordination = client.post(
        "/api/coordinations/", headers=admin_headers, json=decline_body
    )
    assert decline_coordination.status_code == 201
    declined = client.post(
        f"/api/coordinations/{decline_coordination.json()['id']}/respond?response_text=decline",
        headers=donor_headers,
    )
    assert declined.status_code == 200
    assert declined.json()["coordination_status"] == "declined"

    # Donor cannot respond to a non-pending coordination
    # Create a new request so a NEW coordination is created
    control_request = client.post(
        "/api/requests/",
        headers=owner_headers,
        json={
            "blood_group": "A+",
            "units_required": 1,
            "hospital_name": "Control Hospital",
            "city": "Springfield",
        },
    ).json()
    control_body = {
        "request_id": control_request["id"],
        "donor_id": donor["id"],
    }
    contacted_coordination = client.post(
        "/api/coordinations/", headers=admin_headers, json=control_body
    )
    assert contacted_coordination.status_code == 201
    resp = client.post(
        f"/api/coordinations/{contacted_coordination.json()['id']}/respond?response_text=accept",
        headers=donor_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["coordination_status"] == "contacted"
