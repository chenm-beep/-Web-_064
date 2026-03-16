from django.contrib import admin
from .models import OperationLog

@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'target', 'ip', 'created_at']
    list_filter = ['action']
    readonly_fields = ['created_at']
