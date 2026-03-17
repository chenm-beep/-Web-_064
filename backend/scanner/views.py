from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from .models import Site, ScanTask, Vulnerability, Report, POCPlugin, ScanRule, PortScanResult
from .serializers import (
    SiteSerializer, ScanTaskSerializer, VulnerabilitySerializer,
    ReportSerializer, POCPluginSerializer, ScanRuleSerializer, PortScanResultSerializer
)
from users.permissions import IsAdminRole


class SiteViewSet(viewsets.ModelViewSet):
    """网站管理"""
    serializer_class = SiteSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status']
    search_fields = ['name', 'url', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Site.objects.all()
        return Site.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ScanTaskViewSet(viewsets.ModelViewSet):
    """扫描任务管理"""
    serializer_class = ScanTaskSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'scan_type', 'site']
    search_fields = ['name']
    ordering_fields = ['start_time', 'end_time', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return ScanTask.objects.all()
        return ScanTask.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """启动扫描任务"""
        task = self.get_object()
        if task.status == 'running':
            return Response({'error': '任务正在运行中'}, status=status.HTTP_400_BAD_REQUEST)

        task.status = 'running'
        task.start_time = timezone.now()
        task.progress = 0
        task.save()

        # Here you would typically trigger an async task
        # For now, we just mark it as running
        return Response({'message': '任务已启动', 'task_id': task.id})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消扫描任务"""
        task = self.get_object()
        if task.status != 'running':
            return Response({'error': '只能取消运行中的任务'}, status=status.HTTP_400_BAD_REQUEST)

        task.status = 'cancelled'
        task.end_time = timezone.now()
        task.save()
        return Response({'message': '任务已取消'})

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """获取任务进度"""
        task = self.get_object()
        return Response({
            'task_id': task.id,
            'status': task.status,
            'progress': task.progress,
            'vulnerabilities': {
                'critical': task.critical_count,
                'high': task.high_count,
                'medium': task.medium_count,
                'low': task.low_count,
                'info': task.info_count,
            }
        })


class VulnerabilityViewSet(viewsets.ModelViewSet):
    """漏洞管理"""
    serializer_class = VulnerabilitySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['severity', 'vuln_type', 'status', 'task']
    search_fields = ['name', 'url', 'description']
    ordering_fields = ['created_at', 'severity']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Vulnerability.objects.all()
        return Vulnerability.objects.filter(task__created_by=user)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """更新漏洞状态"""
        vulnerability = self.get_object()
        new_status = request.data.get('status')

        if new_status not in ['open', 'fixed', 'ignored']:
            return Response({'error': '无效的状态'}, status=status.HTTP_400_BAD_REQUEST)

        vulnerability.status = new_status
        vulnerability.save()
        return Response({'message': '状态已更新', 'status': new_status})


class ReportViewSet(viewsets.ModelViewSet):
    """报告管理"""
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['task']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Report.objects.all()
        return Report.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """导出报告为Markdown"""
        report = self.get_object()
        return Response({
            'title': report.title,
            'content': report.content,
            'format': 'markdown'
        })


class POCPluginViewSet(viewsets.ModelViewSet):
    """POC插件管理（管理员）"""
    queryset = POCPlugin.objects.all()
    serializer_class = POCPluginSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    filterset_fields = ['vuln_type', 'enabled']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """切换启用状态"""
        plugin = self.get_object()
        plugin.enabled = not plugin.enabled
        plugin.save()
        return Response({
            'message': '状态已切换',
            'enabled': plugin.enabled
        })


class ScanRuleViewSet(viewsets.ModelViewSet):
    """扫描规则管理（管理员）"""
    queryset = ScanRule.objects.all()
    serializer_class = ScanRuleSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    filterset_fields = ['rule_type', 'enabled']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """切换启用状态"""
        rule = self.get_object()
        rule.enabled = not rule.enabled
        rule.save()
        return Response({
            'message': '状态已切换',
            'enabled': rule.enabled
        })


class PortScanViewSet(viewsets.ReadOnlyModelViewSet):
    """端口扫描结果（只读）"""
    serializer_class = PortScanResultSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['task', 'state', 'port']
    search_fields = ['host', 'service']
    ordering_fields = ['port', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return PortScanResult.objects.all()
        return PortScanResult.objects.filter(task__created_by=user)


class DashboardStatsView(APIView):
    """仪表板统计数据"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == 'admin':
            sites = Site.objects.all()
            tasks = ScanTask.objects.all()
            vulnerabilities = Vulnerability.objects.all()
        else:
            sites = Site.objects.filter(owner=user)
            tasks = ScanTask.objects.filter(created_by=user)
            vulnerabilities = Vulnerability.objects.filter(task__created_by=user)

        return Response({
            'sites_count': sites.count(),
            'tasks_count': tasks.count(),
            'vulnerabilities_count': vulnerabilities.count(),
            'running_tasks': tasks.filter(status='running').count(),
            'critical_vulns': vulnerabilities.filter(severity='critical').count(),
            'high_vulns': vulnerabilities.filter(severity='high').count(),
            'medium_vulns': vulnerabilities.filter(severity='medium').count(),
            'low_vulns': vulnerabilities.filter(severity='low').count(),
            'info_vulns': vulnerabilities.filter(severity='info').count(),
        })


class DashboardVulnTrendView(APIView):
    """漏洞趋势数据"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        days = int(request.query_params.get('days', 30))

        if user.role == 'admin':
            vulnerabilities = Vulnerability.objects.all()
        else:
            vulnerabilities = Vulnerability.objects.filter(task__created_by=user)

        # Get data for the last N days
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        trend_data = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            next_date = date + timedelta(days=1)
            count = vulnerabilities.filter(
                created_at__gte=date,
                created_at__lt=next_date
            ).count()
            trend_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })

        return Response(trend_data)


class DashboardVulnTypesView(APIView):
    """漏洞类型分布"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == 'admin':
            vulnerabilities = Vulnerability.objects.all()
        else:
            vulnerabilities = Vulnerability.objects.filter(task__created_by=user)

        # Count vulnerabilities by type
        vuln_types = vulnerabilities.values('vuln_type').annotate(
            count=Count('id')
        ).order_by('-count')

        # Get display names
        type_choices = dict(Vulnerability.VULN_TYPE_CHOICES)
        result = []
        for item in vuln_types:
            result.append({
                'type': item['vuln_type'],
                'name': type_choices.get(item['vuln_type'], item['vuln_type']),
                'count': item['count']
            })

        return Response(result)
