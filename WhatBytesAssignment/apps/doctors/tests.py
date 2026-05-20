import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


pytestmark = pytest.mark.django_db


def authenticated_client():
    user = get_user_model().objects.create_user(name="Admin", email="admin@example.com", password="StrongPass123!")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_doctor_crud_for_authenticated_user():
    client = authenticated_client()

    create_response = client.post(
        "/api/doctors/",
        {
            "name": "Dr. Maya Rao",
            "specialization": "Cardiology",
            "email": "maya.rao@example.com",
            "phone": "9999999999",
        },
        format="json",
    )

    assert create_response.status_code == 201
    doctor_id = create_response.data["id"]

    list_response = client.get("/api/doctors/")
    assert list_response.status_code == 200
    assert len(list_response.data) == 1

    detail_response = client.get(f"/api/doctors/{doctor_id}/")
    assert detail_response.status_code == 200
    assert detail_response.data["specialization"] == "Cardiology"

    update_response = client.put(
        f"/api/doctors/{doctor_id}/",
        {
            "name": "Dr. Maya Rao",
            "specialization": "Neurology",
            "email": "maya.rao@example.com",
            "phone": "9999999999",
        },
        format="json",
    )
    assert update_response.status_code == 200
    assert update_response.data["specialization"] == "Neurology"

    delete_response = client.delete(f"/api/doctors/{doctor_id}/")
    assert delete_response.status_code == 204

