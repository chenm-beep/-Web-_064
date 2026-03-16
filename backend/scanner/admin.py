from django.contrib import admin
from .models import Site, ScanTask, Vulnerability, Report, POCPlugin, ScanRule, PortScanResult

admin.site.register(Site)
admin.site.register(ScanTask)
admin.site.register(Vulnerability)
admin.site.register(Report)
admin.site.register(POCPlugin)
admin.site.register(ScanRule)
admin.site.register(PortScanResult)
