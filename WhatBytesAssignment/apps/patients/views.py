from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import Patient
from .serializers import PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user)

    def get_object(self):
        patient = get_object_or_404(Patient, pk=self.kwargs[self.lookup_field])
        if patient.created_by_id != self.request.user.id:
            raise PermissionDenied("You do not have access to this patient.")
        self.check_object_permissions(self.request, patient)
        return patient

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
