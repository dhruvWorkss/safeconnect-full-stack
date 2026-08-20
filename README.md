# SafeConnect

SafeConnect is a full-stack trust-and-safety moderation platform with a portfolio-grade moderator command center and a production-oriented Django API.

## Stack

- React 19 + TypeScript frontend
- Django 5 + Django REST Framework
- JWT authentication and role-based permissions
- PostgreSQL, Redis, Celery, Docker
- Pytest API and workflow coverage

## Run locally

```bash
docker compose up --build
npm install
npm run dev
```

For a lightweight local backend without Docker:

```bash
cd backend
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Demo moderator: `moderator` / `SafeConnect123!`

Obtain a JWT from `POST /api/auth/token/`, then store the access token as `safeconnect_access` in browser local storage. The dashboard automatically switches from representative demo data to live API cases.

## API surface

- `/api/auth/register/`, `/api/auth/token/`, `/api/auth/token/refresh/`
- `/api/reports/`, `/api/blocks/`, `/api/cases/`
- `/api/cases/{id}/claim/`, `/api/cases/{id}/act/`
- `/api/notifications/`, `/api/audit-logs/`, `/api/dashboard/stats/`

The report workflow prevents duplicate active reports, generates risk-ranked cases, enforces moderator-only access, records immutable audit events, and supports background notifications.
