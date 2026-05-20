import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.doctors.models import Doctor
from apps.patients.models import Patient

from .models import PatientDoctorMapping


pytestmark = pytest.mark.django_db


def make_user(email):
    return get_user_model().objects.create_user(name=email.split("@")[0], email=email, password="StrongPass123!")


def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_mapping_can_be_created_listed_filtered_and_deleted():
    user = make_user("owner@example.com")
    client = authenticated_client(user)
    patient = Patient.objects.create(name="Patient One", age=45, gender="Female", created_by=user)
    doctor = Doctor.objects.create(name="Dr. Shah", specialization="Dermatology", email="shah@example.com")

    create_response = client.post(
        "/api/mappings/",
        {"patient": patient.id, "doctor": doctor.id},
        format="json",
    )

    assert create_response.status_code == 201
    mapping_id = create_response.data["id"]

    list_response = client.get("/api/mappings/")
    assert list_response.status_code == 200
    assert len(list_response.data) == 1

    patient_response = client.get(f"/api/mappings/{patient.id}/")
    assert patient_response.status_code == 200
    assert patient_response.data[0]["doctor"] == doctor.id

    delete_response = client.delete(f"/api/mappings/{mapping_id}/")
    assert delete_response.status_code == 204


def test_mapping_rejects_patient_owned_by_another_user():
    owner = make_user("owner@example.com")
    other = make_user("other@example.com")
    client = authenticated_client(other)
    patient = Patient.objects.create(name="Private", age=50, gender="Male", created_by=owner)
    doctor = Doctor.objects.create(name="Dr. Global", specialization="ENT", email="global@example.com")

    response = client.post(
        "/api/mappings/",
        {"patient": patient.id, "doctor": doctor.id},
        format="json",
    )

    assert response.status_code == 403


def test_mapping_returns_404_for_missing_foreign_keys():
    user = make_user("owner@example.com")
    client = authenticated_client(user)
    doctor = Doctor.objects.create(name="Dr. Global", specialization="ENT", email="global@example.com")

    missing_patient_response = client.post(
        "/api/mappings/",
        {"patient": 9999, "doctor": doctor.id},
        format="json",
    )
    missing_doctor_response = client.post(
        "/api/mappings/",
        {"patient": Patient.objects.create(name="Owned", age=30, gender="Other", created_by=user).id, "doctor": 9999},
        format="json",
    )

    assert missing_patient_response.status_code == 404
    assert missing_doctor_response.status_code == 404


def test_cross_user_patient_mapping_lookup_returns_403():
    owner = make_user("owner@example.com")
    other = make_user("other@example.com")
    client = authenticated_client(other)
    patient = Patient.objects.create(name="Private", age=50, gender="Male", created_by=owner)
    doctor = Doctor.objects.create(name="Dr. Global", specialization="ENT", email="global@example.com")
    PatientDoctorMapping.objects.create(patient=patient, doctor=doctor)

    response = client.get(f"/api/mappings/{patient.id}/")

    assert response.status_code == 403
