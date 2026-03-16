from django.db import models
from django.conf import settings


class Site(models.Model):
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('inactive', '非活跃'),
    ]
    name = models.CharField(max_length=200, verbose_name='站点名称')
    url = models.URLField(max_length=500, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='描述')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sites', verbose_name='所有者')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '站点'
        verbose_name_plural = '站点'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ScanTask(models.Model):
    SCAN_TYPE_CHOICES = [
        ('full', '全面扫描'),
        ('quick', '快速扫描'),
        ('custom', '自定义扫描'),
    ]
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ]
    name = models.CharField(max_length=200, verbose_name='任务名称')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='tasks', verbose_name='站点')
    scan_type = models.CharField(max_length=20, choices=SCAN_TYPE_CHOICES, default='full', verbose_name='扫描类型')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    progress = models.IntegerField(default=0, verbose_name='进度(%)')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks', verbose_name='创建者')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    config = models.JSONField(default=dict, blank=True, verbose_name='扫描配置')
    total_vulns = models.IntegerField(default=0, verbose_name='漏洞总数')
    high_vulns = models.IntegerField(default=0, verbose_name='高危漏洞数')
    medium_vulns = models.IntegerField(default=0, verbose_name='中危漏洞数')
    low_vulns = models.IntegerField(default=0, verbose_name='低危漏洞数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '扫描任务'
        verbose_name_plural = '扫描任务'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Vulnerability(models.Model):
    TYPE_CHOICES = [
        ('sql_injection', 'SQL注入'),
        ('xss', '跨站脚本(XSS)'),
        ('weak_password', '弱密码'),
        ('path_traversal', '路径遍历'),
        ('command_injection', '命令注入'),
        ('csrf', '跨站请求伪造(CSRF)'),
        ('xxe', 'XML外部实体(XXE)'),
        ('ssrf', '服务器端请求伪造(SSRF)'),
        ('file_upload', '文件上传漏洞'),
        ('info_disclosure', '信息泄露'),
        ('open_redirect', '开放重定向'),
        ('other', '其他'),
    ]
    SEVERITY_CHOICES = [
        ('critical', '严重'),
        ('high', '高危'),
        ('medium', '中危'),
        ('low', '低危'),
        ('info', '信息'),
    ]
    STATUS_CHOICES = [
        ('open', '未修复'),
        ('fixed', '已修复'),
        ('ignored', '已忽略'),
    ]
    task = models.ForeignKey(ScanTask, on_delete=models.CASCADE, related_name='vulnerabilities', verbose_name='扫描任务')
    name = models.CharField(max_length=300, verbose_name='漏洞名称')
    vuln_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='other', verbose_name='漏洞类型')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium', verbose_name='严重程度')
    url = models.URLField(max_length=1000, verbose_name='漏洞URL')
    parameter = models.CharField(max_length=200, blank=True, verbose_name='参数')
    payload = models.TextField(blank=True, verbose_name='攻击载荷')
    description = models.TextField(blank=True, verbose_name='漏洞描述')
    solution = models.TextField(blank=True, verbose_name='修复建议')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发现时间')

    class Meta:
        verbose_name = '漏洞'
        verbose_name_plural = '漏洞'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.get_severity_display()})'


class Report(models.Model):
    task = models.ForeignKey(ScanTask, on_delete=models.CASCADE, related_name='reports', verbose_name='扫描任务')
    title = models.CharField(max_length=300, verbose_name='报告标题')
    content = models.TextField(blank=True, verbose_name='报告内容')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports', verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    file_path = models.CharField(max_length=500, blank=True, verbose_name='文件路径')

    class Meta:
        verbose_name = '报告'
        verbose_name_plural = '报告'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class POCPlugin(models.Model):
    name = models.CharField(max_length=200, verbose_name='插件名称')
    description = models.TextField(blank=True, verbose_name='描述')
    vuln_type = models.CharField(max_length=50, verbose_name='漏洞类型')
    code = models.TextField(verbose_name='插件代码')
    version = models.CharField(max_length=20, default='1.0.0', verbose_name='版本')
    enabled = models.BooleanField(default=True, verbose_name='启用')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='poc_plugins', verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = 'POC插件'
        verbose_name_plural = 'POC插件'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ScanRule(models.Model):
    RULE_TYPE_CHOICES = [
        ('regex', '正则表达式'),
        ('keyword', '关键词匹配'),
        ('header', 'HTTP头检测'),
        ('payload', 'Payload测试'),
    ]
    name = models.CharField(max_length=200, verbose_name='规则名称')
    description = models.TextField(blank=True, verbose_name='描述')
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES, default='regex', verbose_name='规则类型')
    content = models.TextField(verbose_name='规则内容')
    enabled = models.BooleanField(default=True, verbose_name='启用')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scan_rules', verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '扫描规则'
        verbose_name_plural = '扫描规则'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class PortScanResult(models.Model):
    STATE_CHOICES = [
        ('open', '开放'),
        ('closed', '关闭'),
        ('filtered', '过滤'),
    ]
    task = models.ForeignKey(ScanTask, on_delete=models.CASCADE, related_name='port_scans', verbose_name='扫描任务')
    host = models.CharField(max_length=200, verbose_name='主机')
    port = models.IntegerField(verbose_name='端口')
    service = models.CharField(max_length=100, blank=True, verbose_name='服务')
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='open', verbose_name='状态')
    banner = models.TextField(blank=True, verbose_name='Banner信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '端口扫描结果'
        verbose_name_plural = '端口扫描结果'
        ordering = ['port']

    def __str__(self):
        return f'{self.host}:{self.port} ({self.service})'
