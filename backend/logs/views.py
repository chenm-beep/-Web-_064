from rest_framework import viewsets, permissions
from .models import OperationLog
from .serializers import OperationLogSerializer


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OperationLog.objects.all().select_related('user')
    serializer_class = OperationLogSerializer
    permission_classes = [IsAdminRole]
    filterset_fields = ['user', 'action']
    search_fields = ['action', 'target']
    ordering_fields = ['created_at']
