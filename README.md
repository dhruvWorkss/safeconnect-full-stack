# SafeConnect

SafeConnect is a full-stack trust and safety platform for social-media companies. It gives moderators a secure, company-isolated workspace for reviewing user reports, prioritising risky cases, taking moderation actions, and maintaining an auditable decision history.

## Live application

- **Frontend:** https://safeconnect-trust-safety.luffyy1707.chatgpt.site
- **Backend health check:** https://safeconnect-api-qyfu.onrender.com/api/health/

### Demo access

| Field | Value |
| --- | --- |
| Company workspace | `nova-social` |
| Employee username | `moderator` |
| Password | `SafeConnect123!` |

These credentials are also shown on the sign-in screen. The backend runs on Render's free tier and may need up to 50 seconds to wake after inactivity.

## Features

- Multi-company workspace authentication with JWT access and refresh tokens
- Tenant-isolated report, case, notification, and audit-log data
- Role-based permissions for users, moderators, and administrators
- Risk-ranked moderation queue with search and severity filtering
- Case details, evidence signals, account context, and risk assessment
- Moderator actions including claim, resolve, dismiss, and escalate
- New-report workflow with validation and duplicate-report protection
- User blocking, notifications, and immutable audit events
- Responsive moderator dashboard for desktop, tablet, and mobile
- PostgreSQL persistence, Redis caching/rate limiting, and Celery support
- Hardened production settings: HSTS, SSL redirect, secure cookies, and enforced password validation
- Unit and integration tests for authentication, validation, permissions, and workflow edge cases

## Technology

| Layer | Technologies |
| --- | --- |
| Frontend | React 19, TypeScript, Vinext/Vite, CSS |
| Backend | Python, Django 5, Django REST Framework |
| Database | PostgreSQL |
| Background services | Redis, Celery |
| Authentication | Simple JWT, role-based permissions |
| Testing | Pytest, pytest-django, DRF test client |
| Infrastructure | Docker Compose, Render, OpenAI Sites |

## Project structure

```text
.
├── app/                 # React/TypeScript dashboard and API proxy
├── worker/              # Cloudflare Worker entry point for the frontend
├── backend/
│   ├── moderation/      # Models, serializers, permissions, views, and tests
│   ├── safeconnect/     # Django configuration, URLs, Celery, and WSGI
│   ├── Dockerfile       # Django production container
│   └── manage.py
├── public/              # Frontend static assets
├── docker-compose.yml   # Local PostgreSQL, Redis, backend, and worker services
└── render.yaml          # Render backend and PostgreSQL blueprint
```

## Run locally

### Requirements

- Node.js 22.13+
- Python 3.12+
- Docker Desktop (recommended for the complete stack)

### 1. Start the backend services

```bash
docker compose up --build
```

The Django API will be available at `http://localhost:8000/api/`.

### 2. Start the frontend

In a second terminal:

```bash
npm install
npm run dev
```

Open the local URL printed by the development server and use the demo credentials above.

### Backend without Docker

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## API overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health/` | Service health check |
| `POST` | `/api/auth/token/` | Workspace login and JWT creation |
| `POST` | `/api/auth/token/refresh/` | Refresh an access token |
| `GET/POST` | `/api/reports/` | List or create reports |
| `GET/POST` | `/api/blocks/` | Manage user blocks |
| `GET` | `/api/cases/` | Retrieve the moderator case queue |
| `POST` | `/api/cases/{id}/claim/` | Assign a case to the current moderator |
| `POST` | `/api/cases/{id}/act/` | Resolve, dismiss, or escalate a case |
| `GET` | `/api/notifications/` | Retrieve workspace notifications |
| `GET` | `/api/audit-logs/` | Retrieve moderation audit events |
| `GET` | `/api/dashboard/stats/` | Retrieve dashboard metrics |

Protected routes require an access token:

```http
Authorization: Bearer <access-token>
```

## Testing

```bash
cd backend
pytest                 # 7 tests
```

The test suite covers workspace authentication, tenant isolation, report validation, duplicate reports, moderator permissions, moderation actions, and audit-log creation.

Frontend checks:

```bash
npx tsc --noEmit       # type check
npm run build          # production build
```

## Security

Production settings are enforced whenever `DEBUG` is off:

- `DJANGO_SECRET_KEY` is required — the app refuses to start without it rather than falling back to a development key
- HSTS (1 year, subdomains, preload), SSL redirect, and secure session/CSRF cookies
- `SECURE_PROXY_SSL_HEADER` is set so the SSL redirect works behind Render's TLS-terminating proxy
- Django's full password-validator set is enabled
- JWT access tokens last 30 minutes; refresh tokens rotate and are blacklisted after use
- DRF throttling caps anonymous requests at 30/min and authenticated requests at 120/min

`python manage.py check --deploy` reports no issues.

## Deployment

- `render.yaml` provisions the Django web service and PostgreSQL database on Render.
- The frontend uses a same-origin server proxy at `/api/backend/*` to communicate securely with the deployed Django API.
- Production CORS and allowed-host settings are restricted to the deployed SafeConnect domains.
- Required backend environment variables: `DATABASE_URL`, `DJANGO_SECRET_KEY`, `DEBUG=0`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`. `render.yaml` wires all five, generating the secret key automatically.

## Portfolio summary

Built a production-style moderation platform using Django REST Framework, React, TypeScript, and PostgreSQL for user reporting, blocking, risk-based case triage, moderator actions, notifications, and auditable case-resolution workflows.
