import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import Patient


pytestmark = pytest.mark.django_db


def authenticated_client(email="owner@example.com"):
    user = get_user_model().objects.create_user(name="Owner", email=email, password="StrongPass123!")
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


def test_protected_patient_endpoint_requires_authentication():
    response = APIClient().get("/api/patients/")

    assert response.status_code == 401


def test_patient_crud_is_scoped_to_authenticated_user():
    client, owner = authenticated_client()

    create_response = client.post(
        "/api/patients/",
        {"name": "Jane Doe", "age": 31, "gender": "Female", "medical_history": "Asthma"},
        format="json",
    )

    assert create_response.status_code == 201
    patient_id = create_response.data["id"]
    assert create_response.data["created_by"] == owner.id

    list_response = client.get("/api/patients/")
    assert list_response.status_code == 200
    assert len(list_response.data) == 1

    update_response = client.put(
        f"/api/patients/{patient_id}/",
        {"name": "Jane A. Doe", "age": 32, "gender": "Female", "medical_history": "Asthma"},
        format="json",
    )
    assert update_response.status_code == 200
    assert update_response.data["age"] == 32

    delete_response = client.delete(f"/api/patients/{patient_id}/")
    assert delete_response.status_code == 204


def test_cross_user_patient_access_returns_403():
    owner_client, owner = authenticated_client("owner@example.com")
    other_client, _ = authenticated_client("other@example.com")
    patient = Patient.objects.create(name="Private Patient", age=40, gender="Male", created_by=owner)

    owner_list = owner_client.get("/api/patients/")
    other_list = other_client.get("/api/patients/")
    detail_response = other_client.get(f"/api/patients/{patient.id}/")

    assert owner_list.status_code == 200
    assert len(owner_list.data) == 1
    assert other_list.status_code == 200
    assert other_list.data == []
    assert detail_response.status_code == 403


def test_patient_age_must_be_reasonable():
    client, _ = authenticated_client()

    response = client.post(
        "/api/patients/",
        {"name": "Invalid Age", "age": 131, "gender": "Other"},
        format="json",
    )

    assert response.status_code == 400
    assert "age" in response.data

