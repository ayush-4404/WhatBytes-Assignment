from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.doctors.models import Doctor
from apps.doctors.serializers import DoctorSerializer
from apps.patients.models import Patient
from apps.patients.serializers import PatientSerializer

from .models import PatientDoctorMapping


class OwnedPatientPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Patient.objects.filter(created_by=request.user)
        return Patient.objects.none()

    def to_internal_value(self, data):
        try:
            patient = Patient.objects.get(pk=data)
        except (TypeError, ValueError, Patient.DoesNotExist):
            raise NotFound("Patient not found.")
        request = self.context.get("request")
        if request and patient.created_by_id != request.user.id:
            raise PermissionDenied("You do not have access to this patient.")
        return patient


class DoctorPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    queryset = Doctor.objects.all()

    def to_internal_value(self, data):
        try:
            return Doctor.objects.get(pk=data)
        except (TypeError, ValueError, Doctor.DoesNotExist):
            raise NotFound("Doctor not found.")


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    patient = OwnedPatientPrimaryKeyRelatedField()
    doctor = DoctorPrimaryKeyRelatedField()
    patient_details = PatientSerializer(source="patient", read_only=True)
    doctor_details = DoctorSerializer(source="doctor", read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ("id", "patient", "doctor", "patient_details", "doctor_details", "assigned_at")
        read_only_fields = ("id", "patient_details", "doctor_details", "assigned_at")

    def validate_patient(self, patient):
        request = self.context.get("request")
        if request and patient.created_by_id != request.user.id:
            raise serializers.ValidationError("You do not have access to this patient.")
        return patient

    def validate(self, attrs):
        patient = attrs.get("patient") or getattr(self.instance, "patient", None)
        doctor = attrs.get("doctor") or getattr(self.instance, "doctor", None)
        if patient and doctor:
            exists = PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor)
            if self.instance:
                exists = exists.exclude(pk=self.instance.pk)
            if exists.exists():
                raise serializers.ValidationError("This doctor is already assigned to the patient.")
        return attrs
