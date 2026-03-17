from django.contrib import admin
from .models import OperationLog


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'resource', 'resource_id', 'ip_address', 'created_at')
    list_filter = ('action', 'resource', 'created_at')
    search_fields = ('description', 'resource', 'ip_address')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'action', 'resource', 'resource_id', 'description',
                       'ip_address', 'user_agent', 'created_at')
