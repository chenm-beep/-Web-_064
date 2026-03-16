# 智能Web应用漏洞扫描系统

一个面向开发者和安全工程师的轻量化、高兼容、可扩展的Web应用漏洞扫描平台。

## 系统概述

本系统基于 Django + Vue.js 前后端分离架构，集成分布式爬虫、POC漏洞验证与安全基线核查技术，
实现 Web 应用漏洞自动化发现、分级评估与合规审计功能，支持 OWASP Top 10、CVE 等主流漏洞标准。

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + ECharts |
| 后端 | Python Django 4.x + Django REST Framework |
| 认证 | JWT (djangorestframework-simplejwt) |
| 数据库 | SQLite (开发) / MySQL (生产) |
| 缓存 | Redis（可选） |
| 部署 | Docker + Nginx |

## 功能模块

### 普通用户功能
- **总览仪表盘**：安全态势统计、漏洞趋势图表、最新任务动态
- **资产管理**：录入和管理待扫描的 Web 站点
- **扫描任务**：创建扫描任务、查看扫描进度、实时获取扫描状态
- **漏洞报告**：查看漏洞详情、按风险等级筛选、跟踪修复状态
- **端口扫描**：查看端口扫描结果

### 管理员功能（在普通功能基础上）
- **POC插件库**：维护漏洞验证 POC 脚本，支持自定义插件上传
- **扫描规则**：配置扫描规则集，支持自定义合规基线
- **用户管理**：创建和管理系统用户，分配权限角色
- **操作日志**：审计所有用户操作记录

## 快速开始

### 方式一：Docker 一键部署（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd <project-directory>

# 一键启动
docker-compose up -d

# 访问系统
# 前端：http://localhost
# 后端 API：http://localhost:8000
```

### 方式二：手动部署

#### 后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 初始化示例数据
python manage.py seed_data

# 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 生产构建
npm run build
```

## 默认账户

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 普通用户 | test | test123 |

> ⚠️ 生产环境请务必修改默认密码

## API 文档

后端启动后访问 `http://localhost:8000/api/` 查看可用端点。

### 主要 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login/` | 用户登录，返回 JWT token |
| POST | `/api/auth/logout/` | 退出登录 |
| GET | `/api/auth/me/` | 获取当前用户信息 |
| GET/POST | `/api/sites/` | 站点列表/创建 |
| GET/POST | `/api/tasks/` | 扫描任务列表/创建 |
| POST | `/api/tasks/{id}/start/` | 启动扫描任务 |
| POST | `/api/tasks/{id}/cancel/` | 取消扫描任务 |
| GET | `/api/vulnerabilities/` | 漏洞列表（支持筛选） |
| GET | `/api/dashboard/stats/` | 仪表盘统计数据 |
| GET | `/api/dashboard/vuln-trend/` | 漏洞趋势数据 |
| GET | `/api/dashboard/vuln-types/` | 漏洞类型分布 |
| GET/POST | `/api/poc-plugins/` | POC插件管理（管理员） |
| GET/POST | `/api/scan-rules/` | 扫描规则管理（管理员） |
| GET | `/api/logs/` | 操作日志（管理员） |

## 项目结构

```
.
├── backend/                 # Django 后端
│   ├── config/              # 全局配置（settings, urls）
│   ├── users/               # 用户认证模块
│   ├── scanner/             # 核心扫描模块
│   │   ├── models.py        # 数据模型
│   │   ├── views.py         # API 视图
│   │   ├── simulate.py      # 扫描模拟引擎
│   │   └── management/      # 管理命令
│   ├── logs/                # 操作日志模块
│   ├── requirements.txt
│   └── manage.py
├── frontend/                # Vue.js 前端
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   ├── layouts/         # 布局组件
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── router/          # Vue Router 路由
│   │   └── utils/           # 工具函数
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

## 漏洞检测能力

系统支持检测以下 OWASP Top 10 及常见漏洞类型：

- SQL 注入（SQL Injection）
- 跨站脚本攻击（XSS）
- 跨站请求伪造（CSRF）
- 路径遍历（Path Traversal）
- 弱密码（Weak Password）
- 文件上传漏洞（File Upload）
- 命令注入（Command Injection）
- 敏感信息泄露（Information Disclosure）
- 不安全的直接对象引用（IDOR）
- 安全配置错误（Security Misconfiguration）
- 不安全的反序列化（Insecure Deserialization）
- XXE 注入（XML External Entity）

## 环境要求

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose（可选）

## License

本项目为毕业设计作品，仅供学习研究使用。