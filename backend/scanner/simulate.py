"""
Simulate scan execution - creates fake vulnerabilities and port scan results
for demonstration purposes.
"""
import random


FAKE_VULNERABILITIES = [
    {
        'name': 'SQL注入漏洞',
        'vuln_type': 'sql_injection',
        'severity': 'high',
        'parameter': 'id',
        'payload': "' OR '1'='1",
        'description': '在参数id中发现SQL注入漏洞，攻击者可能通过此漏洞获取数据库中的敏感信息。',
        'solution': '使用参数化查询或预编译语句，对用户输入进行严格验证和过滤。',
    },
    {
        'name': '反射型XSS漏洞',
        'vuln_type': 'xss',
        'severity': 'medium',
        'parameter': 'search',
        'payload': '<script>alert("XSS")</script>',
        'description': '在搜索参数中发现反射型XSS漏洞，攻击者可以通过构造恶意链接执行任意JavaScript代码。',
        'solution': '对所有用户输入进行HTML编码，实施内容安全策略(CSP)。',
    },
    {
        'name': '存储型XSS漏洞',
        'vuln_type': 'xss',
        'severity': 'high',
        'parameter': 'comment',
        'payload': '<img src=x onerror=alert(1)>',
        'description': '在评论功能中发现存储型XSS漏洞，恶意代码被持久存储并对所有访问者执行。',
        'solution': '对存储的用户内容进行严格的HTML过滤和编码，使用白名单验证。',
    },
    {
        'name': '弱密码漏洞',
        'vuln_type': 'weak_password',
        'severity': 'medium',
        'parameter': 'password',
        'payload': 'admin123',
        'description': '系统存在弱密码，使用常见密码组合可以成功登录管理员账户。',
        'solution': '实施强密码策略，要求包含大小写字母、数字和特殊字符，长度不少于8位。',
    },
    {
        'name': '路径遍历漏洞',
        'vuln_type': 'path_traversal',
        'severity': 'high',
        'parameter': 'file',
        'payload': '../../../etc/passwd',
        'description': '文件下载接口存在路径遍历漏洞，攻击者可以读取服务器上的任意文件。',
        'solution': '验证和规范化文件路径，使用白名单限制可访问的目录和文件。',
    },
    {
        'name': 'CSRF跨站请求伪造',
        'vuln_type': 'csrf',
        'severity': 'medium',
        'parameter': '',
        'payload': '',
        'description': '敏感操作接口未实施CSRF防护，攻击者可以诱导用户执行非预期的操作。',
        'solution': '在所有状态变更请求中实施CSRF令牌验证，使用SameSite Cookie属性。',
    },
    {
        'name': 'SSRF服务器端请求伪造',
        'vuln_type': 'ssrf',
        'severity': 'high',
        'parameter': 'url',
        'payload': 'http://169.254.169.254/latest/meta-data/',
        'description': '发现SSRF漏洞，攻击者可以利用服务器访问内网资源或云服务元数据。',
        'solution': '验证和过滤用户提供的URL，禁止访问内网地址和敏感服务。',
    },
    {
        'name': '敏感信息泄露',
        'vuln_type': 'info_disclosure',
        'severity': 'low',
        'parameter': '',
        'payload': '',
        'description': '服务器响应头中泄露了详细的版本信息，可能帮助攻击者定向利用已知漏洞。',
        'solution': '隐藏或删除服务器响应中的版本信息，配置适当的安全响应头。',
    },
    {
        'name': '开放重定向漏洞',
        'vuln_type': 'open_redirect',
        'severity': 'low',
        'parameter': 'redirect',
        'payload': 'https://evil.com',
        'description': '重定向参数未经验证，攻击者可以将用户重定向到恶意网站进行钓鱼攻击。',
        'solution': '验证重定向URL，只允许重定向到本站域名下的URL。',
    },
    {
        'name': '文件上传漏洞',
        'vuln_type': 'file_upload',
        'severity': 'critical',
        'parameter': 'file',
        'payload': 'shell.php',
        'description': '文件上传接口未限制上传文件类型，攻击者可上传恶意脚本文件。',
        'solution': '严格限制上传文件类型，对文件内容进行验证，将上传目录设置为不可执行。',
    },
    {
        'name': 'XXE外部实体注入',
        'vuln_type': 'xxe',
        'severity': 'high',
        'parameter': 'xml',
        'payload': '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>',
        'description': 'XML解析器允许外部实体，攻击者可以读取本地文件或发起SSRF攻击。',
        'solution': '禁用XML解析器的外部实体功能，使用安全的XML解析库配置。',
    },
    {
        'name': '命令注入漏洞',
        'vuln_type': 'command_injection',
        'severity': 'critical',
        'parameter': 'host',
        'payload': '; cat /etc/passwd',
        'description': '在ping功能中发现命令注入漏洞，攻击者可以在服务器上执行任意系统命令。',
        'solution': '避免将用户输入直接传递给系统命令，使用安全的API替代shell命令执行。',
    },
]

FAKE_PORTS = [
    {'port': 80, 'service': 'http', 'banner': 'Apache/2.4.41 (Ubuntu)'},
    {'port': 443, 'service': 'https', 'banner': 'nginx/1.18.0'},
    {'port': 22, 'service': 'ssh', 'banner': 'OpenSSH 8.2p1 Ubuntu'},
    {'port': 3306, 'service': 'mysql', 'banner': 'MySQL 8.0.32'},
    {'port': 8080, 'service': 'http-proxy', 'banner': 'Apache Tomcat/9.0.65'},
    {'port': 6379, 'service': 'redis', 'banner': 'Redis 7.0.5'},
    {'port': 27017, 'service': 'mongodb', 'banner': 'MongoDB 6.0.3'},
    {'port': 5432, 'service': 'postgresql', 'banner': 'PostgreSQL 14.7'},
    {'port': 21, 'service': 'ftp', 'banner': 'vsftpd 3.0.3'},
    {'port': 25, 'service': 'smtp', 'banner': 'Postfix smtpd'},
]


def simulate_scan(task):
    """
    Simulate a vulnerability scan by creating fake vulnerabilities and port scan results.
    """
    from django.utils import timezone as dj_timezone
    from .models import Vulnerability, PortScanResult

    task.status = 'running'
    task.start_time = dj_timezone.now()
    task.progress = 0
    task.save()

    try:
        site_url = task.site.url.rstrip('/')

        num_ports = random.randint(3, 7)
        selected_ports = random.sample(FAKE_PORTS, num_ports)
        for port_info in selected_ports:
            PortScanResult.objects.create(
                task=task,
                host=site_url.split('//')[-1].split('/')[0],
                port=port_info['port'],
                service=port_info['service'],
                state='open',
                banner=port_info['banner'],
            )

        task.progress = 30
        task.save()

        num_vulns = random.randint(5, 15)
        selected_vulns = random.choices(FAKE_VULNERABILITIES, k=num_vulns)

        paths = ['/login', '/search', '/admin', '/api/users', '/upload', '/download', '/profile', '/comment']

        for vuln_template in selected_vulns:
            path = random.choice(paths)
            vuln_url = f"{site_url}{path}"
            Vulnerability.objects.create(
                task=task,
                name=vuln_template['name'],
                vuln_type=vuln_template['vuln_type'],
                severity=vuln_template['severity'],
                url=vuln_url,
                parameter=vuln_template['parameter'],
                payload=vuln_template['payload'],
                description=vuln_template['description'],
                solution=vuln_template['solution'],
                status='open',
            )

        task.progress = 80
        task.save()

        vulns = task.vulnerabilities.all()
        task.total_vulns = vulns.count()
        task.high_vulns = vulns.filter(severity__in=['high', 'critical']).count()
        task.medium_vulns = vulns.filter(severity='medium').count()
        task.low_vulns = vulns.filter(severity__in=['low', 'info']).count()
        task.status = 'completed'
        task.end_time = dj_timezone.now()
        task.progress = 100
        task.save()

    except Exception as e:
        task.status = 'failed'
        task.save()
        raise e

    return task
