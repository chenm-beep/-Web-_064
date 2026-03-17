from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import OperationLog
from .serializers import OperationLogSerializer
from users.permissions import IsAdminRole


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """操作日志（只读，管理员）"""
    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    filterset_fields = ['action', 'resource', 'user']
    search_fields = ['description', 'resource']
    ordering_fields = ['created_at']
