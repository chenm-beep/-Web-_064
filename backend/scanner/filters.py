import django_filters
from .models import ScanTask, Vulnerability, Site


class SiteFilter(django_filters.FilterSet):
    class Meta:
        model = Site
        fields = ['status', 'owner']


class ScanTaskFilter(django_filters.FilterSet):
    class Meta:
        model = ScanTask
        fields = ['status', 'scan_type', 'site', 'created_by']


class VulnerabilityFilter(django_filters.FilterSet):
    class Meta:
        model = Vulnerability
        fields = ['vuln_type', 'severity', 'status', 'task']
