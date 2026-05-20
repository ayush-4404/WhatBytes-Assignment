import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


pytestmark = pytest.mark.django_db


def test_user_can_register_and_login():
    client = APIClient()

    register_response = client.post(
        "/api/auth/register/",
        {"name": "Ayush Admin", "email": "ayush@example.com", "password": "StrongPass123!"},
        format="json",
    )

    assert register_response.status_code == 201
    assert register_response.data["email"] == "ayush@example.com"
    assert "password" not in register_response.data

    login_response = client.post(
        "/api/auth/login/",
        {"email": "ayush@example.com", "password": "StrongPass123!"},
        format="json",
    )

    assert login_response.status_code == 200
    assert "access" in login_response.data
    assert "refresh" in login_response.data


def test_duplicate_email_registration_returns_validation_error():
    User = get_user_model()
    User.objects.create_user(name="Existing", email="dupe@example.com", password="StrongPass123!")

    response = APIClient().post(
        "/api/auth/register/",
        {"name": "Duplicate", "email": "dupe@example.com", "password": "StrongPass123!"},
        format="json",
    )

    assert response.status_code == 400
    assert "email" in response.data


def test_invalid_login_returns_401_error():
    response = APIClient().post(
        "/api/auth/login/",
        {"email": "missing@example.com", "password": "wrong-password"},
        format="json",
    )

    assert response.status_code == 401
