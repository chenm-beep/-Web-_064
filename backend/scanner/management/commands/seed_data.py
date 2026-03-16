import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from scanner.models import Site, ScanTask, Vulnerability, Report, POCPlugin, ScanRule, PortScanResult
from scanner.simulate import simulate_scan, FAKE_VULNERABILITIES
from logs.models import OperationLog

User = get_user_model()


class Command(BaseCommand):
    help = '填充示例数据'

    def handle(self, *args, **options):
        self.stdout.write('开始创建示例数据...')

        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('✓ 创建管理员用户: admin/admin123'))
        else:
            self.stdout.write('- 管理员用户已存在')

        test_user, created = User.objects.get_or_create(
            username='test',
            defaults={
                'email': 'test@example.com',
                'role': 'user',
            }
        )
        if created:
            test_user.set_password('test123')
            test_user.save()
            self.stdout.write(self.style.SUCCESS('✓ 创建普通用户: test/test123'))
        else:
            self.stdout.write('- 普通用户已存在')

        sites_data = [
            {
                'name': '企业官网',
                'url': 'https://www.example.com',
                'description': '公司官方网站，包含产品介绍和联系信息',
                'owner': admin,
            },
            {
                'name': '内部管理系统',
                'url': 'http://internal.example.com:8080',
                'description': '内部ERP管理系统，包含敏感业务数据',
                'owner': admin,
            },
            {
                'name': '用户测试站点',
                'url': 'https://test-app.example.com',
                'description': '测试用户的Web应用',
                'owner': test_user,
            },
        ]

        sites = []
        for site_data in sites_data:
            site, created = Site.objects.get_or_create(
                url=site_data['url'],
                defaults=site_data
            )
            sites.append(site)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ 创建站点: {site.name}'))

        tasks_config = [
            {'name': '企业官网全面扫描', 'site': sites[0], 'user': admin, 'scan_type': 'full', 'run': True},
            {'name': '内部系统快速扫描', 'site': sites[1], 'user': admin, 'scan_type': 'quick', 'run': True},
            {'name': '企业官网二次扫描', 'site': sites[0], 'user': admin, 'scan_type': 'full', 'run': True},
            {'name': '测试站点扫描', 'site': sites[2], 'user': test_user, 'scan_type': 'quick', 'run': True},
            {'name': '待执行扫描任务', 'site': sites[1], 'user': admin, 'scan_type': 'custom', 'run': False},
        ]

        tasks = []
        for task_config in tasks_config:
            task, created = ScanTask.objects.get_or_create(
                name=task_config['name'],
                defaults={
                    'site': task_config['site'],
                    'created_by': task_config['user'],
                    'scan_type': task_config['scan_type'],
                    'status': 'pending',
                    'config': {'timeout': 30, 'max_depth': 5},
                }
            )
            tasks.append(task)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ 创建任务: {task.name}'))
                if task_config['run']:
                    try:
                        simulate_scan(task)
                        task.refresh_from_db()
                        self.stdout.write(f'  → 扫描完成，发现 {task.total_vulns} 个漏洞')
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'  → 模拟扫描出错: {e}'))

        poc_plugins_data = [
            {
                'name': 'SQL注入检测插件',
                'description': '检测常见的SQL注入漏洞，包括联合注入、盲注等',
                'vuln_type': 'sql_injection',
                'code': '# SQL注入检测POC\ndef check(url, param):\n    payloads = ["\' OR \'1\'=\'1"]\n    return False, None\n',
                'version': '1.2.0',
                'enabled': True,
                'created_by': admin,
            },
            {
                'name': 'XSS漏洞检测插件',
                'description': '检测反射型和DOM型XSS漏洞',
                'vuln_type': 'xss',
                'code': '# XSS检测POC\ndef check(url, param):\n    payloads = ["<script>alert(1)</script>"]\n    return False, None\n',
                'version': '1.1.0',
                'enabled': True,
                'created_by': admin,
            },
            {
                'name': '路径遍历检测插件',
                'description': '检测路径遍历和文件包含漏洞',
                'vuln_type': 'path_traversal',
                'code': '# 路径遍历检测POC\ndef check(url, param):\n    payloads = ["../../../etc/passwd"]\n    return False, None\n',
                'version': '1.0.0',
                'enabled': True,
                'created_by': admin,
            },
        ]

        for poc_data in poc_plugins_data:
            poc, created = POCPlugin.objects.get_or_create(
                name=poc_data['name'],
                defaults=poc_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ 创建POC插件: {poc.name}'))

        scan_rules_data = [
            {
                'name': 'SQL错误信息检测规则',
                'description': '通过检测响应中的SQL错误信息来发现SQL注入漏洞',
                'rule_type': 'regex',
                'content': r'(mysql_fetch_array|ORA-\d{5}|Microsoft OLE DB)',
                'enabled': True,
                'created_by': admin,
            },
            {
                'name': '敏感文件路径检测',
                'description': '检测是否存在敏感文件和目录',
                'rule_type': 'keyword',
                'content': '/.env\n/.git/config\n/wp-config.php',
                'enabled': True,
                'created_by': admin,
            },
            {
                'name': '安全响应头检测',
                'description': '检测是否缺少重要的安全响应头',
                'rule_type': 'header',
                'content': 'X-Frame-Options\nX-XSS-Protection\nContent-Security-Policy',
                'enabled': True,
                'created_by': admin,
            },
        ]

        for rule_data in scan_rules_data:
            rule, created = ScanRule.objects.get_or_create(
                name=rule_data['name'],
                defaults=rule_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ 创建扫描规则: {rule.name}'))

        completed_tasks = ScanTask.objects.filter(status='completed')
        for task in completed_tasks:
            report, created = Report.objects.get_or_create(
                task=task,
                defaults={
                    'title': f'{task.name} - 安全扫描报告',
                    'content': f'本报告是对 {task.site.url} 进行安全扫描的结果汇总。',
                    'created_by': task.created_by,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ 创建报告: {report.title}'))

        log_actions = [
            ('用户登录', '系统', admin),
            ('创建扫描任务', '企业官网全面扫描', admin),
            ('启动扫描', '企业官网全面扫描', admin),
            ('查看漏洞详情', 'SQL注入漏洞', admin),
            ('导出报告', '企业官网全面扫描报告', admin),
            ('用户登录', '系统', test_user),
            ('创建站点', '测试站点', test_user),
        ]

        for action_name, target, user in log_actions:
            OperationLog.objects.get_or_create(
                user=user,
                action=action_name,
                target=target,
                defaults={'details': {}, 'ip': '127.0.0.1'}
            )

        self.stdout.write(self.style.SUCCESS('\n✅ 示例数据创建完成！'))
        self.stdout.write('账号信息:')
        self.stdout.write('  管理员: admin / admin123')
        self.stdout.write('  普通用户: test / test123')

        self.stdout.write(f'\n数据统计:')
        self.stdout.write(f'  站点数量: {Site.objects.count()}')
        self.stdout.write(f'  任务数量: {ScanTask.objects.count()}')
        self.stdout.write(f'  漏洞数量: {Vulnerability.objects.count()}')
        self.stdout.write(f'  POC插件: {POCPlugin.objects.count()}')
        self.stdout.write(f'  扫描规则: {ScanRule.objects.count()}')
