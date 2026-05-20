from django.urls import path

from .views import PatientDoctorMappingDetailView, PatientDoctorMappingListCreateView

urlpatterns = [
    path("", PatientDoctorMappingListCreateView.as_view(), name="mapping-list-create"),
    path("<int:patient_id>/", PatientDoctorMappingDetailView.as_view(), name="mapping-detail"),
]
