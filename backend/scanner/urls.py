from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SiteViewSet, ScanTaskViewSet, VulnerabilityViewSet, ReportViewSet,
    POCPluginViewSet, ScanRuleViewSet, PortScanViewSet,
    DashboardStatsView, DashboardVulnTrendView, DashboardVulnTypesView
)

router = DefaultRouter()
router.register(r'sites', SiteViewSet, basename='site')
router.register(r'tasks', ScanTaskViewSet, basename='task')
router.register(r'vulnerabilities', VulnerabilityViewSet, basename='vulnerability')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'poc-plugins', POCPluginViewSet, basename='poc-plugin')
router.register(r'scan-rules', ScanRuleViewSet, basename='scan-rule')
router.register(r'port-scans', PortScanViewSet, basename='port-scan')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/vuln-trend/', DashboardVulnTrendView.as_view(), name='dashboard-vuln-trend'),
    path('dashboard/vuln-types/', DashboardVulnTypesView.as_view(), name='dashboard-vuln-types'),
]
