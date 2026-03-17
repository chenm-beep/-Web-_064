from django.db import models
from django.conf import settings


class Site(models.Model):
    """网站信息"""
    STATUS_CHOICES = (
        ('active', '活跃'),
        ('inactive', '未活跃'),
    )

    name = models.CharField('网站名称', max_length=200)
    url = models.URLField('网站URL', max_length=500)
    description = models.TextField('描述', blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='所有者')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sites'
        verbose_name = '网站'
        verbose_name_plural = '网站'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ScanTask(models.Model):
    """扫描任务"""
    SCAN_TYPE_CHOICES = (
        ('full', '全面扫描'),
        ('quick', '快速扫描'),
        ('custom', '自定义扫描'),
    )
    STATUS_CHOICES = (
        ('pending', '等待中'),
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    )

    name = models.CharField('任务名称', max_length=200)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='目标网站', related_name='tasks')
    scan_type = models.CharField('扫描类型', max_length=20, choices=SCAN_TYPE_CHOICES, default='full')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField('进度', default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='创建者')
    start_time = models.DateTimeField('开始时间', null=True, blank=True)
    end_time = models.DateTimeField('结束时间', null=True, blank=True)
    config = models.JSONField('配置', default=dict, blank=True)

    # Vulnerability counts
    critical_count = models.IntegerField('严重漏洞数', default=0)
    high_count = models.IntegerField('高危漏洞数', default=0)
    medium_count = models.IntegerField('中危漏洞数', default=0)
    low_count = models.IntegerField('低危漏洞数', default=0)
    info_count = models.IntegerField('信息漏洞数', default=0)

    class Meta:
        db_table = 'scan_tasks'
        verbose_name = '扫描任务'
        verbose_name_plural = '扫描任务'
        ordering = ['-start_time', '-id']

    def __str__(self):
        return self.name


class Vulnerability(models.Model):
    """漏洞信息"""
    VULN_TYPE_CHOICES = (
        ('sql_injection', 'SQL注入'),
        ('xss', '跨站脚本'),
        ('weak_password', '弱口令'),
        ('path_traversal', '路径遍历'),
        ('command_injection', '命令注入'),
        ('csrf', '跨站请求伪造'),
        ('xxe', 'XML外部实体注入'),
        ('ssrf', '服务端请求伪造'),
        ('file_upload', '文件上传漏洞'),
        ('info_disclosure', '信息泄露'),
        ('open_redirect', '开放重定向'),
        ('other', '其他'),
    )
    SEVERITY_CHOICES = (
        ('critical', '严重'),
        ('high', '高危'),
        ('medium', '中危'),
        ('low', '低危'),
        ('info', '信息'),
    )
    STATUS_CHOICES = (
        ('open', '未修复'),
        ('fixed', '已修复'),
        ('ignored', '已忽略'),
    )

    name = models.CharField('漏洞名称', max_length=200)
    task = models.ForeignKey(ScanTask, on_delete=models.CASCADE, verbose_name='扫描任务', related_name='vulnerabilities')
    vuln_type = models.CharField('漏洞类型', max_length=50, choices=VULN_TYPE_CHOICES)
    severity = models.CharField('严重程度', max_length=20, choices=SEVERITY_CHOICES)
    url = models.URLField('漏洞URL', max_length=1000)
    parameter = models.CharField('参数', max_length=200, blank=True)
    payload = models.TextField('攻击载荷', blank=True)
    description = models.TextField('描述', blank=True)
    solution = models.TextField('解决方案', blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'vulnerabilities'
        verbose_name = '漏洞'
        verbose_name_plural = '漏洞'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Report(models.Model):
    """扫描报告"""
    task = models.ForeignKey(ScanTask, on_delete=models.CASCADE, verbose_name='扫描任务', related_name='reports')
    title = models.CharField('报告标题', max_length=200)
    content = models.TextField('报告内容', blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    file_path = models.CharField('文件路径', max_length=500, blank=True)

    class Meta:
        db_table = 'reports'
        verbose_name = '报告'
        verbose_name_plural = '报告'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class POCPlugin(models.Model):
    """POC插件"""
    name = models.CharField('插件名称', max_length=200)
    description = models.TextField('描述', blank=True)
    vuln_type = models.CharField('漏洞类型', max_length=50)
    code = models.TextField('插件代码')
    version = models.CharField('版本', max_length=50, default='1.0')
    enabled = models.BooleanField('启用状态', default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'poc_plugins'
        verbose_name = 'POC插件'
        verbose_name_plural = 'POC插件'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ScanRule(models.Model):
    """扫描规则"""
    RULE_TYPE_CHOICES = (
        ('regex', '正则表达式'),
        ('keyword', '关键词'),
        ('header', '响应头'),
        ('payload', '攻击载荷'),
    )

    name = models.CharField('规则名称', max_length=200)
    description = models.TextField('描述', blank=True)
    rule_type = models.CharField('规则类型', max_length=20, choices=RULE_TYPE_CHOICES)
    content = models.TextField('规则内容')
    enabled = models.BooleanField('启用状态', default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'scan_rules'
        verbose_name = '扫描规则'
        verbose_name_plural = '扫描规则'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class PortScanResult(models.Model):
    """端口扫描结果"""
    STATE_CHOICES = (
        ('open', '开放'),
        ('closed', '关闭'),
        ('filtered', '过滤'),
    )

    task = models.ForeignKey(ScanTask, on_delete=models.CASCADE, verbose_name='扫描任务', related_name='port_scans')
    host = models.CharField('主机', max_length=200)
    port = models.IntegerField('端口')
    service = models.CharField('服务', max_length=100, blank=True)
    state = models.CharField('状态', max_length=20, choices=STATE_CHOICES)
    banner = models.TextField('横幅', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'port_scan_results'
        verbose_name = '端口扫描结果'
        verbose_name_plural = '端口扫描结果'
        ordering = ['port']

    def __str__(self):
        return f'{self.host}:{self.port}'
