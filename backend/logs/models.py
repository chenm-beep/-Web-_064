from django.db import models
from django.conf import settings


class OperationLog(models.Model):
    """操作日志"""
    ACTION_CHOICES = (
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('login', '登录'),
        ('logout', '登出'),
        ('other', '其他'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             null=True, verbose_name='操作用户')
    action = models.CharField('操作类型', max_length=20, choices=ACTION_CHOICES)
    resource = models.CharField('资源类型', max_length=100)
    resource_id = models.CharField('资源ID', max_length=100, blank=True)
    description = models.TextField('描述', blank=True)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'operation_logs'
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.action} - {self.resource}'
