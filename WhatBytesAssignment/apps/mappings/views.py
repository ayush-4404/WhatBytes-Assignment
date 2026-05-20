from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.patients.models import Patient

from .models import PatientDoctorMapping
from .serializers import PatientDoctorMappingSerializer


class PatientDoctorMappingListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientDoctorMappingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            PatientDoctorMapping.objects.select_related("patient", "doctor")
            .filter(patient__created_by=self.request.user)
        )


class PatientDoctorMappingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id)
        if patient.created_by_id != request.user.id:
            raise PermissionDenied("You do not have access to this patient.")
        mappings = PatientDoctorMapping.objects.select_related("patient", "doctor").filter(patient=patient)
        serializer = PatientDoctorMappingSerializer(mappings, many=True, context={"request": request})
        return Response(serializer.data)

    def delete(self, request, patient_id):
        mapping = get_object_or_404(
            PatientDoctorMapping.objects.select_related("patient", "doctor"),
            pk=patient_id,
        )
        if mapping.patient.created_by_id != request.user.id:
            raise PermissionDenied("You do not have access to this mapping.")
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
