# Ticket Management App

A full-stack ticket/case management web application built for a senior engineering take-home assessment. The backend uses Django REST Framework with Celery for asynchronous email notifications, while the frontend is built with SvelteKit, TypeScript, and Tailwind CSS v4.

## Project Overview

This application allows teams to manage support tickets through a role-based system (ADMIN, MANAGER, AGENT). Key features include:

- **Ticket management** — Create, assign, and update tickets with priority and status tracking
- **Real-time notifications** — In-app notifications with async email delivery via Celery
- **Audit logging** — Complete history of all changes made to tickets
- **Role-based access control** — Different permissions for ADMIN, MANAGER, and AGENT roles
- **JWT authentication** — Secure API access with token-based auth
- **API documentation** — Interactive Swagger UI and ReDoc for API exploration

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | SvelteKit + TypeScript + Tailwind CSS v4 | Modern, reactive UI |
| Backend | Django 5 + Django REST Framework | RESTful API server |
| Database | PostgreSQL 16 | Primary data store |
| Cache | Redis 7 | Caching layer + Celery result backend |
| Broker | Redis 7 | Celery task queue broker |
| Background tasks | Celery 5 | Async email notifications |
| Containers | Docker + Docker Compose | Development environment |
| Testing | pytest + factory-boy + pytest-cov | Backend testing |
| Linting | Ruff | Python code quality |

### Architecture

The backend follows a clean **Service → Selector → Serializer → View** architecture:

```
View (API endpoint)
  └── Serializer (validation & data transformation)
        └── Selector (business logic queries)
              └── Service (database operations & side effects)
```

This separation ensures:
- **Views** only handle HTTP concerns
- **Selectors** encapsulate query logic
- **Services** manage database operations and trigger side effects (like notifications)

## Installation & Setup

### Prerequisites

- Docker Desktop or Docker Engine + Docker Compose
- Git

### 1. Clone the repository

```bash
git clone <repo-url>
cd Simple_Ticket_Management_App
```

### 2. Configure environment variables

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit backend/.env — at minimum set a strong SECRET_KEY
```

### 3. Start all services

```bash
make up
```

This starts:
- **PostgreSQL** (port 5432)
- **Redis** (port 6379)
- **Django backend** (port 8000)
- **Celery worker** (background task processing)
- **SvelteKit frontend** (port 5173)

### 4. Run database migrations

```bash
make migrate
```

### 5. Load sample data (optional)

```bash
make seed
```

### 6. Create an admin user

```bash
make createsuperuser
```

### 7. Access the application

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api/ |
| Swagger UI | http://localhost:8000/api/docs/ |
| Django Admin | http://localhost:8000/admin/ |

---

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit .env
python manage.py migrate
python manage.py runserver
```

In a separate terminal, start the Celery worker:

```bash
cd backend
source .venv/bin/activate
celery -A core worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

---

## Celery Integration

### Before & After

```
BEFORE (Synchronous):
┌─────────────────────────────────────────────────────────┐
│  User creates ticket                                    │
│      ↓                                                  │
│  Django creates database record                         │
│      ↓                                                  │
│  Django sends email (BLOCKS for 1-5 seconds)           │
│      ↓                                                  │
│  Response returned to user                              │
│                                                         │
│  ❌ User waits for email to send                        │
│  ❌ If email fails, entire request fails                │
│  ❌ No retry mechanism                                  │
│  ❌ Email errors visible to user                        │
└─────────────────────────────────────────────────────────┘

AFTER (Asynchronous with Celery):
┌─────────────────────────────────────────────────────────┐
│  User creates ticket                                    │
│      ↓                                                  │
│  Django creates database record                         │
│      ↓                                                  │
│  Django enqueues email task (50ms)                      │
│      ↓                                                  │
│  Response returned to user immediately                  │
│      ↓                                                  │
│  Celery worker processes email in background            │
│      ↓                                                  │
│  Auto-retry on failure (3 attempts, exponential backoff)│
│      ↓                                                  │
│  Notification status updated: PENDING → SENT / FAILED   │
│                                                         │
│  ✅ User gets instant response                          │
│  ✅ Email failures don't affect user experience         │
│  ✅ Automatic retry with backoff                        │
│  ✅ Delivery status tracking                            │
└─────────────────────────────────────────────────────────┘
```

### Benefits of Celery

| Aspect | Before (Sync) | After (Celery) |
|---|---|---|
| **Response time** | 1-5s (email send) | ~50ms (task enqueue) |
| **User experience** | Blocking, slow | Instant feedback |
| **Email failures** | Request fails | Auto-retry, user unaffected |
| **Retry mechanism** | Manual or none | Automatic (3 attempts, exponential backoff) |
| **Status tracking** | None | PENDING → SENT / FAILED |
| **Scalability** | Limited by email server | Horizontal scaling via workers |
| **Resource usage** | Tied to web process | Separate worker processes |

### How It Works

1. **Task Definition** (`apps/notifications/tasks.py`):
   ```python
   @shared_task(
       bind=True,
       autoretry_for=(Exception,),
       retry_backoff=True,
       max_retries=3,
   )
   def send_notification_email(self, notification_id, recipient_email, ...):
       # Send email and update notification status
   ```

2. **Task Enqueueing** (`apps/notifications/services.py`):
   ```python
   def create_notification(*, ticket, user, type):
       notification = Notification.objects.create(...)
       send_notification_email.delay(  # Non-blocking!
           notification_id=str(notification.id),
           recipient_email=user.email,
           ...
       )
       return notification
   ```

3. **Email Builder** (`apps/notifications/email.py`):
   - Separates email content generation from task logic
   - Reusable for different notification types
   - Easy to test and maintain

### Configuration

- **Broker**: Redis (`redis://localhost:6379/0`)
- **Result Backend**: Redis (`redis://localhost:6379/0`)
- **Task Serialization**: JSON
- **Retry Policy**: Exponential backoff, max 3 retries
- **Hard Limit**: 30 minutes per task

---

## Testing

### Backend Tests

```bash
# Run all tests with coverage
make test-backend

# Run specific test suite
cd backend
pytest apps/notifications/ -v
pytest apps/tickets/ -v
pytest apps/comments/ -v
```

**Test Coverage**: 135 tests across all apps
- Accounts: 20 tests
- Audit: 14 tests
- Comments: 25 tests
- Notifications: 43 tests (includes Celery task tests)
- Tickets: 33 tests

### Linting

```bash
make lint-backend    # ruff check + ruff format --check
make lint-frontend   # prettier + eslint
```

---

## Project Structure

```
.
├── backend/                  # Django project
│   ├── core/                 # Project config (settings, urls, celery, asgi, wsgi)
│   ├── apps/                 # Feature apps
│   │   ├── accounts/         # User management & authentication
│   │   ├── tickets/          # Ticket CRUD & management
│   │   ├── comments/         # Ticket comments
│   │   ├── notifications/    # In-app notifications + Celery email tasks
│   │   └── audit/            # Audit logging
│   ├── fixtures/             # Sample data (JSON fixtures)
│   ├── logs/                 # Rotating log files (gitignored)
│   ├── media/                # User-uploaded files (gitignored)
│   ├── staticfiles/          # Collected static files (gitignored)
│   ├── conftest.py           # pytest fixtures & Celery test config
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pytest.ini
│   └── ruff.toml
│
├── frontend/                 # SvelteKit application
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api/          # HTTP client layer
│   │   │   ├── components/   # Reusable UI components
│   │   │   ├── stores/       # Svelte stores (global state)
│   │   │   ├── types/        # TypeScript interfaces
│   │   │   ├── utils/        # Pure helper functions
│   │   │   └── constants/    # App-wide constants
│   │   └── routes/
│   │       ├── (app)/        # Authenticated pages (dashboard, tickets, profile)
│   │       └── (auth)/       # Public pages (login, register)
│   ├── static/
│   └── Dockerfile
│
├── images/                   # Documentation images (ERD, etc.)
├── .github/workflows/ci.yml  # GitHub Actions CI
├── docker-compose.yml
├── Makefile
├── .editorconfig
└── README.md
```

---

## Entity Relationship Diagram (ERD)

The database schema design is structured as follows:

![Entity Relationship Diagram](./images/ERD.png)

---

## Git Branching Strategy

To keep the development organized and align with the assessment guidelines, the repository uses the following branch structure:

- **`main`**: Production-ready release branch.
- **`dev`**: Integration branch for development features.
- **`feature/*`**: Topic branches for implementing new requirements (e.g., `feature/dashboard`, `feature/tickets`).
- **`fix/*`**: Bugfix branches for resolving issues (e.g., `fix/cors-headers`, `fix/celery-imports`).

---

## Makefile Commands

Run `make help` to see all available commands:

| Command | Description |
|---|---|
| `make up` | Start all services |
| `make down` | Stop all services |
| `make build` | Build / rebuild all images |
| `make logs` | Tail logs for all services |
| `make migrate` | Apply database migrations |
| `make createsuperuser` | Create a Django admin superuser |
| `make seed` | Seed database with sample data |
| `make test-backend` | Run backend tests with coverage |
| `make lint-backend` | Lint & format-check backend with ruff |
| `make format-backend` | Auto-format backend with ruff |
| `make lint-frontend` | Lint & format-check frontend |
| `make test-frontend` | Run frontend tests |

---

## Email Notifications (Gmail SMTP)

### Environment Variables

Configure these in `backend/.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_google_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

> **Note:** `EMAIL_HOST_PASSWORD` is a [Google App Password](https://myaccount.google.com/apppasswords), not your regular Gmail password. Never commit `.env` to Git.

### How It Works

```
User action (create/update ticket, add comment)
        ↓
create_notification() saves record + calls send_notification_email.delay()
        ↓
Redis queues the task
        ↓
Celery worker picks it up
        ↓
Django send_mail() sends via Gmail SMTP
        ↓
Notification.status → SENT (or FAILED on error)
```

### Testing Email Notifications

1. **Start Redis and the Celery worker:**
   ```bash
   make up                    # starts Redis + worker via Docker
   # — or locally —
   redis-server               # start Redis
   cd backend && celery -A core worker --loglevel=info  # start worker
   ```

2. **Create a ticket or comment** that triggers a notification (e.g., assign a ticket to a user).

3. **Check the recipient's inbox** — the email should arrive from your configured `DEFAULT_FROM_EMAIL`.

4. **Check notification status** in Django admin (`/admin/notifications/notification/`):
   - `status = SENT` and `sent_at` populated → email delivered
   - `status = FAILED` → check Celery worker logs for the error

---

## Redis Caching

Redis is used for three purposes in this project:

| Purpose | Redis DB | Config |
|---|---|---|
| Celery broker | `0` | `CELERY_BROKER_URL` |
| Celery result backend | `0` | `CELERY_RESULT_BACKEND` |
| Django cache | `1` | `REDIS_URL` |

### Cached Endpoints

| Endpoint | Cache Key | Timeout | Description |
|---|---|---|---|
| `GET /api/tickets/dashboard_stats/` | `dashboard_stats` | 5 min | Aggregate ticket counts (total, open, in-progress, closed, priority breakdown) |
| `GET /api/tickets/my_stats/` | `my_stats_{user_id}` | 5 min | Per-user assigned/created ticket stats |

### How It Works

```
First request (cache miss):
  GET /api/tickets/dashboard_stats/
        ↓
  Query database (7 aggregate queries)
        ↓
  Cache response in Redis (key: "dashboard_stats", TTL: 300s)
        ↓
  Return response

Second request (cache hit):
  GET /api/tickets/dashboard_stats/
        ↓
  Return cached response instantly (no DB queries)
```

### Cache Invalidation

Cache is automatically invalidated when ticket data changes. Only affected keys are deleted — `cache.clear()` is never used.

| Event | Keys Invalidated |
|---|---|
| Ticket created | `dashboard_stats`, `my_stats_{creator}`, `my_stats_{assignee}` |
| Ticket updated | `dashboard_stats`, `my_stats_{creator}`, `my_stats_{assignee}` |
| Ticket deleted | `dashboard_stats`, `my_stats_{creator}`, `my_stats_{assignee}` |
| Assignment changed | `dashboard_stats`, `my_stats_{old_assignee}`, `my_stats_{new_assignee}` |

If the creator and assignee are the same user, only one `my_stats_*` key is deleted.

### Configuration

The cache backend is configured in `settings.py`:

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://localhost:6379/1"),
    }
}
```

Set `REDIS_URL` in `backend/.env`:

```env
REDIS_URL=redis://localhost:6379/1
```

### Testing

Run cache-specific tests:

```bash
cd backend
pytest apps/tickets/tests.py::TestDashboardCache -v
```

Tests verify:
- First request queries DB and populates cache
- Second request returns cached data
- Cache invalidates after ticket create, update, delete, and assignment changes
- Each user gets their own `my_stats_*` cache entry

---

## Assumptions & Notes

- JWT is used for API authentication.
- Google OAuth is planned via `django-allauth` (not yet implemented).
- Redis serves as Celery broker/result backend and Django cache (DB 0 for Celery, DB 1 for cache).
- Email is sent via Gmail SMTP (configured in `.env`).
- Celery tasks auto-retry on failure with exponential backoff (3 attempts).
- Notification status tracks email delivery: PENDING → SENT / FAILED.
- No Celery Beat (periodic tasks) — all tasks are triggered by user actions.
- `SENTRY_DSN` left empty disables Sentry; set it to activate monitoring.
