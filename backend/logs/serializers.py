from rest_framework import serializers
from .models import OperationLog


class OperationLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = OperationLog
        fields = ['id', 'user', 'username', 'action', 'target', 'details', 'ip', 'created_at']
        read_only_fields = ['created_at']
