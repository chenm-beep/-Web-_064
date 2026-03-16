from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Q
from django.utils import timezone
from django.http import HttpResponse

from .models import Site, ScanTask, Vulnerability, Report, POCPlugin, ScanRule, PortScanResult
from .serializers import (
    SiteSerializer, ScanTaskSerializer, VulnerabilitySerializer,
    ReportSerializer, POCPluginSerializer, ScanRuleSerializer, PortScanResultSerializer
)
from .filters import SiteFilter, ScanTaskFilter, VulnerabilityFilter
from .simulate import simulate_scan


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class SiteViewSet(viewsets.ModelViewSet):
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = SiteFilter
    search_fields = ['name', 'url', 'description']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Site.objects.all().select_related('owner')
        return Site.objects.filter(owner=user).select_related('owner')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ScanTaskViewSet(viewsets.ModelViewSet):
    serializer_class = ScanTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ScanTaskFilter
    search_fields = ['name']
    ordering_fields = ['created_at', 'status', 'progress']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return ScanTask.objects.all().select_related('site', 'created_by')
        return ScanTask.objects.filter(created_by=user).select_related('site', 'created_by')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        task = self.get_object()
        if task.status not in ['pending', 'failed', 'cancelled']:
            return Response(
                {'detail': f'任务状态为{task.get_status_display()}，无法启动'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            simulate_scan(task)
            task.refresh_from_db()
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': f'扫描失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        task = self.get_object()
        if task.status not in ['pending', 'running']:
            return Response(
                {'detail': f'任务状态为{task.get_status_display()}，无法取消'},
                status=status.HTTP_400_BAD_REQUEST
            )
        task.status = 'cancelled'
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        task = self.get_object()
        return Response({
            'id': task.id,
            'status': task.status,
            'progress': task.progress,
            'total_vulns': task.total_vulns,
        })


class VulnerabilityViewSet(viewsets.ModelViewSet):
    serializer_class = VulnerabilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = VulnerabilityFilter
    search_fields = ['name', 'url', 'description']
    ordering_fields = ['created_at', 'severity', 'status']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Vulnerability.objects.all().select_related('task', 'task__site')
        return Vulnerability.objects.filter(
            task__created_by=user
        ).select_related('task', 'task__site')

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        vuln = self.get_object()
        new_status = request.data.get('status')
        if new_status not in ['open', 'fixed', 'ignored']:
            return Response({'detail': '无效的状态值'}, status=status.HTTP_400_BAD_REQUEST)
        vuln.status = new_status
        vuln.save()
        serializer = self.get_serializer(vuln)
        return Response(serializer.data)


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['title']
    ordering_fields = ['created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Report.objects.all().select_related('task', 'created_by')
        return Report.objects.filter(created_by=user).select_related('task', 'created_by')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        report = self.get_object()
        task = report.task
        vulns = task.vulnerabilities.all()

        content = f"# {report.title}\n\n"
        content += f"**扫描任务**: {task.name}\n"
        content += f"**站点URL**: {task.site.url}\n"
        content += f"**扫描状态**: {task.get_status_display()}\n"
        content += f"**创建时间**: {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += f"## 漏洞统计\n\n"
        content += f"- 总计: {task.total_vulns}\n"
        content += f"- 高危: {task.high_vulns}\n"
        content += f"- 中危: {task.medium_vulns}\n"
        content += f"- 低危: {task.low_vulns}\n\n"
        content += f"## 漏洞详情\n\n"

        for vuln in vulns:
            content += f"### {vuln.name}\n"
            content += f"- 类型: {vuln.get_vuln_type_display()}\n"
            content += f"- 严重程度: {vuln.get_severity_display()}\n"
            content += f"- URL: {vuln.url}\n"
            if vuln.parameter:
                content += f"- 参数: {vuln.parameter}\n"
            content += f"- 描述: {vuln.description}\n"
            content += f"- 修复建议: {vuln.solution}\n\n"

        response = HttpResponse(content, content_type='text/markdown; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="report_{report.id}.md"'
        return response


class POCPluginViewSet(viewsets.ModelViewSet):
    serializer_class = POCPluginSerializer
    permission_classes = [IsAdminRole]
    search_fields = ['name', 'description', 'vuln_type']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        return POCPlugin.objects.all().select_related('created_by')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        plugin = self.get_object()
        plugin.enabled = not plugin.enabled
        plugin.save()
        return Response({'detail': '插件状态已更新', 'enabled': plugin.enabled})


class ScanRuleViewSet(viewsets.ModelViewSet):
    serializer_class = ScanRuleSerializer
    permission_classes = [IsAdminRole]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        return ScanRule.objects.all().select_related('created_by')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        rule = self.get_object()
        rule.enabled = not rule.enabled
        rule.save()
        return Response({'detail': '规则状态已更新', 'enabled': rule.enabled})


class PortScanViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PortScanResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['task', 'state', 'service']
    ordering_fields = ['port', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return PortScanResult.objects.all().select_related('task')
        return PortScanResult.objects.filter(
            task__created_by=user
        ).select_related('task')


class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'admin':
            tasks_qs = ScanTask.objects.all()
            vulns_qs = Vulnerability.objects.all()
            sites_qs = Site.objects.all()
        else:
            tasks_qs = ScanTask.objects.filter(created_by=user)
            vulns_qs = Vulnerability.objects.filter(task__created_by=user)
            sites_qs = Site.objects.filter(owner=user)

        stats = {
            'total_sites': sites_qs.count(),
            'total_tasks': tasks_qs.count(),
            'running_tasks': tasks_qs.filter(status='running').count(),
            'completed_tasks': tasks_qs.filter(status='completed').count(),
            'total_vulns': vulns_qs.count(),
            'high_vulns': vulns_qs.filter(severity__in=['high', 'critical']).count(),
            'medium_vulns': vulns_qs.filter(severity='medium').count(),
            'low_vulns': vulns_qs.filter(severity__in=['low', 'info']).count(),
            'open_vulns': vulns_qs.filter(status='open').count(),
            'fixed_vulns': vulns_qs.filter(status='fixed').count(),
        }
        return Response(stats)


class DashboardVulnTrendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from django.db.models.functions import TruncDate
        from datetime import timedelta

        user = request.user
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        if user.role == 'admin':
            vulns_qs = Vulnerability.objects.filter(created_at__gte=start_date)
        else:
            vulns_qs = Vulnerability.objects.filter(
                task__created_by=user, created_at__gte=start_date
            )

        trend = (
            vulns_qs
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(
                total=Count('id'),
                high=Count('id', filter=Q(severity__in=['high', 'critical'])),
                medium=Count('id', filter=Q(severity='medium')),
                low=Count('id', filter=Q(severity__in=['low', 'info'])),
            )
            .order_by('date')
        )

        return Response(list(trend))


class DashboardVulnTypesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'admin':
            vulns_qs = Vulnerability.objects.all()
        else:
            vulns_qs = Vulnerability.objects.filter(task__created_by=user)

        types = (
            vulns_qs
            .values('vuln_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        result = []
        type_map = dict(Vulnerability.TYPE_CHOICES)
        for item in types:
            result.append({
                'type': item['vuln_type'],
                'name': type_map.get(item['vuln_type'], item['vuln_type']),
                'count': item['count'],
            })

        return Response(result)
