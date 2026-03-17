from django.contrib import admin
from .models import Site, ScanTask, Vulnerability, Report, POCPlugin, ScanRule, PortScanResult


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'owner', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'url', 'description')
    ordering = ('-created_at',)


@admin.register(ScanTask)
class ScanTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'site', 'scan_type', 'status', 'progress', 'start_time')
    list_filter = ('status', 'scan_type', 'start_time')
    search_fields = ('name', 'site__name')
    ordering = ('-start_time',)


@admin.register(Vulnerability)
class VulnerabilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'vuln_type', 'severity', 'status', 'created_at')
    list_filter = ('severity', 'vuln_type', 'status', 'created_at')
    search_fields = ('name', 'url', 'description')
    ordering = ('-created_at',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'task', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'content')
    ordering = ('-created_at',)


@admin.register(POCPlugin)
class POCPluginAdmin(admin.ModelAdmin):
    list_display = ('name', 'vuln_type', 'version', 'enabled', 'created_at')
    list_filter = ('enabled', 'vuln_type', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)


@admin.register(ScanRule)
class ScanRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'rule_type', 'enabled', 'created_at')
    list_filter = ('enabled', 'rule_type', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)


@admin.register(PortScanResult)
class PortScanResultAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'service', 'state', 'created_at')
    list_filter = ('state', 'created_at')
    search_fields = ('host', 'service')
    ordering = ('port',)
