from rest_framework import serializers
from .models import OperationLog


class OperationLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = OperationLog
        fields = ('id', 'user', 'user_name', 'action', 'resource', 'resource_id',
                  'description', 'ip_address', 'user_agent', 'created_at')
        read_only_fields = ('id', 'created_at')
