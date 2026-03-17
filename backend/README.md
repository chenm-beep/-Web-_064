# Web Vulnerability Scanner Backend

Django REST Framework backend for a web vulnerability scanning system.

## Features

- JWT Authentication
- Site Management
- Scan Task Management
- Vulnerability Tracking
- Reports Generation
- POC Plugin Management
- Scan Rules Management
- Port Scan Results
- Dashboard Statistics and Analytics

## Installation

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Create a superuser:
```bash
python manage.py createsuperuser
```

4. Start the development server:
```bash
python manage.py runserver 0.0.0.0:8000
```

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Logout and blacklist refresh token
- `GET /api/auth/me/` - Get current user info
- `POST /api/auth/change-password/` - Change password

### Scanner
- `GET/POST /api/scanner/sites/` - List/Create sites
- `GET/POST /api/scanner/tasks/` - List/Create scan tasks
- `GET/POST /api/scanner/vulnerabilities/` - List/Create vulnerabilities
- `GET/POST /api/scanner/reports/` - List/Create reports
- `GET /api/scanner/port-scans/` - List port scan results
- `GET /api/scanner/dashboard/stats/` - Dashboard statistics
- `GET /api/scanner/dashboard/vuln-trend/` - Vulnerability trend data
- `GET /api/scanner/dashboard/vuln-types/` - Vulnerability type distribution

### Admin Only
- `GET/POST /api/scanner/poc-plugins/` - Manage POC plugins
- `GET/POST /api/scanner/scan-rules/` - Manage scan rules
- `GET/POST /api/users/` - User management
- `GET /api/logs/` - Operation logs

## Default Credentials

- Username: admin
- Password: admin123
- Email: admin@example.com

## Technology Stack

- Django 4.2
- Django REST Framework
- djangorestframework-simplejwt
- django-cors-headers
- django-filter
