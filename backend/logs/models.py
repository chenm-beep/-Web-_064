from django.db import models
from django.conf import settings


class OperationLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='operation_logs',
        verbose_name='用户'
    )
    action = models.CharField(max_length=200, verbose_name='操作')
    target = models.CharField(max_length=200, blank=True, verbose_name='操作对象')
    details = models.JSONField(default=dict, blank=True, verbose_name='详情')
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.action} - {self.created_at}'
