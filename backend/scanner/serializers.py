from rest_framework import serializers
from .models import Site, ScanTask, Vulnerability, Report, POCPlugin, ScanRule, PortScanResult


class SiteSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Site
        fields = ('id', 'name', 'url', 'description', 'owner', 'owner_name',
                  'status', 'task_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_task_count(self, obj):
        return obj.tasks.count()


class ScanTaskSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source='site.name', read_only=True)
    site_url = serializers.CharField(source='site.url', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    vulnerability_count = serializers.SerializerMethodField()

    class Meta:
        model = ScanTask
        fields = ('id', 'name', 'site', 'site_name', 'site_url', 'scan_type',
                  'status', 'progress', 'created_by', 'created_by_name',
                  'start_time', 'end_time', 'config', 'critical_count',
                  'high_count', 'medium_count', 'low_count', 'info_count',
                  'vulnerability_count')
        read_only_fields = ('id', 'status', 'progress', 'start_time', 'end_time',
                            'critical_count', 'high_count', 'medium_count',
                            'low_count', 'info_count')

    def get_vulnerability_count(self, obj):
        return obj.vulnerabilities.count()


class VulnerabilitySerializer(serializers.ModelSerializer):
    task_name = serializers.CharField(source='task.name', read_only=True)
    site_name = serializers.CharField(source='task.site.name', read_only=True)
    severity_label = serializers.CharField(source='get_severity_display', read_only=True)
    vuln_type_label = serializers.CharField(source='get_vuln_type_display', read_only=True)

    class Meta:
        model = Vulnerability
        fields = ('id', 'name', 'task', 'task_name', 'site_name', 'vuln_type',
                  'vuln_type_label', 'severity', 'severity_label', 'url',
                  'parameter', 'payload', 'description', 'solution', 'status',
                  'created_at')
        read_only_fields = ('id', 'created_at')


class ReportSerializer(serializers.ModelSerializer):
    task_name = serializers.CharField(source='task.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Report
        fields = ('id', 'task', 'task_name', 'title', 'content', 'created_by',
                  'created_by_name', 'created_at', 'file_path')
        read_only_fields = ('id', 'created_at', 'file_path')


class POCPluginSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = POCPlugin
        fields = ('id', 'name', 'description', 'vuln_type', 'code', 'version',
                  'enabled', 'created_by', 'created_by_name', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ScanRuleSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = ScanRule
        fields = ('id', 'name', 'description', 'rule_type', 'content', 'enabled',
                  'created_by', 'created_by_name', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class PortScanResultSerializer(serializers.ModelSerializer):
    task_name = serializers.CharField(source='task.name', read_only=True)

    class Meta:
        model = PortScanResult
        fields = ('id', 'task', 'task_name', 'host', 'port', 'service',
                  'state', 'banner', 'created_at')
        read_only_fields = ('id', 'created_at')
