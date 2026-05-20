from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Patient
        fields = ("id", "name", "age", "gender", "medical_history", "created_by", "created_at")
        read_only_fields = ("id", "created_by", "created_at")

    def validate_age(self, value):
        if value < 1 or value > 130:
            raise serializers.ValidationError("Age must be between 1 and 130.")
        return value

