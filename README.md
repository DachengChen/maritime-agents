# maritime-agent-saas

A production-oriented but simple SaaS starter for maritime intelligence monitoring and scheduled AI-generated email reports.

## Features

- FastAPI API with task lifecycle endpoints
- PostgreSQL-ready SQLAlchemy models and Alembic setup
- Scheduler-driven periodic execution with APScheduler
- AI report generation service using mock maritime tools
- Email delivery service with Jinja2 templates (mock or SMTP)
- Automated tests for task creation, run-now flow, report generation, and email sending (mocked)

## Project Structure

```text
app/
  main.py
  config.py
  database.py
  models/
  schemas/
  routers/
  services/
  agents/
  tools/
  workers/
  templates/
tests/
```

## Quick Start

### 1) Setup environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

### 2) Run the API

```bash
uvicorn app.main:app --reload
```

Health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

### 3) API Endpoints

- `GET /health`
- `POST /tasks`
- `GET /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`
- `POST /tasks/{task_id}/run-now`
- `GET /reports/{task_id}/latest`

Example task payload:

```json
{
  "email": "ops@example.com",
  "requirement_text": "Monitor container congestion and weather risks in Asia",
  "schedule": "daily 07:00",
  "timezone": "UTC",
  "preferred_report_language": "en"
}
```

## Database and Migrations

This service is configured for PostgreSQL via `DATABASE_URL`.

Run Alembic commands after updating `.env`:

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

## Scheduling and Workers

- APScheduler polls active tasks every minute and runs tasks when schedules match.
- Task execution currently runs in-process through `app/workers/task_worker.py`.
- TODO: Move execution to Celery or RQ for distributed background workers.

## Email Delivery

- `EMAIL_DELIVERY_MODE=mock` logs emails without sending.
- Set `EMAIL_DELIVERY_MODE=smtp` and SMTP variables to send real emails.
- TODO: Add Resend/SendGrid provider integration.

## Running Tests

```bash
pytest
```
