# maritime-agents

A **multi-agent maritime intelligence system** built with Python 3.11+, FastAPI, and LangGraph. The system runs scheduled tasks, collects data from multiple sources (news, AIS vessel tracking, port operations, weather), analyses them through specialised AI agents, and generates a daily Markdown intelligence report.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [API Endpoints](#api-endpoints)
- [Running Tests](#running-tests)
- [Future Extensions](#future-extensions)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Supervisor Agent                  │
│  (orchestrates the workflow; also available as a    │
│   LangGraph StateGraph in daily_report_workflow.py) │
└──────┬──────────┬────────────┬───────────┬──────────┘
       │          │            │           │
  ┌────▼───┐ ┌────▼───┐ ┌─────▼──┐ ┌──────▼──────┐
  │  News  │ │  AIS   │ │  Port  │ │   Weather   │
  │ Agent  │ │ Agent  │ │ Agent  │ │    Agent    │
  └────┬───┘ └────┬───┘ └─────┬──┘ └──────┬──────┘
       └──────────┴────────────┴───────────┘
                        │
                 ┌──────▼──────┐
                 │ Report Agent│
                 └──────┬──────┘
                        │
              ┌─────────▼──────────┐
              │  Markdown Report   │
              │  (+ optional email)│
              └────────────────────┘
```

Each specialist agent delegates to a dedicated **tool** module which can be swapped from mock data to a real API/database by following the `TODO` comments in the source.

---

## Project Structure

```
maritime-agents/
├── app/
│   ├── config.py          # Pydantic Settings (reads .env)
│   ├── main.py            # FastAPI app + endpoints
│   └── scheduler.py       # APScheduler daily cron job
│
├── agents/
│   ├── supervisor_agent.py  # Coordinates all agents
│   ├── news_agent.py        # Fetches maritime/shipping news
│   ├── ais_agent.py         # Checks vessel positions & anomalies
│   ├── port_agent.py        # Checks port congestion & berths
│   ├── weather_agent.py     # Checks weather risks
│   └── report_agent.py      # Assembles the final report
│
├── tools/
│   ├── news_api.py          # News API integration (mock → real)
│   ├── ais_db.py            # AIS/vessel data (mock → real)
│   ├── port_db.py           # Port DB queries (mock → real)
│   ├── weather_api.py       # Weather API integration (mock → real)
│   └── email_tool.py        # SMTP email delivery
│
├── workflows/
│   └── daily_report_workflow.py  # LangGraph StateGraph pipeline
│
├── models/
│   ├── maritime_models.py   # Domain models (vessels, ports, weather)
│   └── report_models.py     # Agent result + report models
│
├── tests/
│   └── test_daily_report_workflow.py
│
├── .env.example
├── pyproject.toml
└── README.md
```

---

## Requirements

- Python 3.11 or later
- `pip` / `pip3`

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/DachengChen/maritime-agents.git
cd maritime-agents

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install the package and its dependencies
pip install -e ".[dev]"

# 4. Copy the example environment file
cp .env.example .env
# Edit .env to add your API keys (optional – mock data works without keys)
```

---

## Configuration

All settings are controlled via environment variables (or a `.env` file).  See `.env.example` for the full list.

| Variable | Default | Description |
|---|---|---|
| `APP_HOST` | `0.0.0.0` | Bind address for the FastAPI server |
| `APP_PORT` | `8000` | Listen port |
| `NEWS_API_KEY` | *(none)* | News API key (mock used if absent) |
| `AIS_API_KEY` | *(none)* | AIS provider key (mock used if absent) |
| `PORT_DB_URL` | `sqlite:///./maritime.db` | SQLAlchemy URL for port database |
| `WEATHER_API_KEY` | *(none)* | Weather API key (mock used if absent) |
| `SMTP_HOST` | *(none)* | SMTP server hostname for email delivery |
| `EMAIL_TO` | *(none)* | Comma-separated report recipient list |
| `REPORTS_DIR` | `./reports` | Directory where Markdown reports are saved |

---

## Running Locally

```bash
# Start the FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.  Interactive API docs are at `http://localhost:8000/docs`.

### Trigger a report manually

```bash
curl -X POST http://localhost:8000/run/daily-report
```

### Retrieve the latest report (JSON)

```bash
curl http://localhost:8000/reports/latest
```

### Retrieve the latest report (Markdown)

```bash
curl "http://localhost:8000/reports/latest?format=markdown"
```

### Run the workflow directly (without the API server)

```python
from agents.supervisor_agent import run_supervisor

report = run_supervisor()
print(report.markdown_content)
```

Or using the LangGraph graph:

```python
from workflows.daily_report_workflow import build_workflow, WorkflowState

graph = build_workflow()
result = graph.invoke(WorkflowState())
print(result["report"].markdown_content)
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `POST` | `/run/daily-report` | Trigger the daily report workflow |
| `GET` | `/reports/latest` | Retrieve the latest report (`?format=markdown`) |

---

## Running Tests

```bash
pytest
```

For verbose output:

```bash
pytest -v
```

---

## Future Extensions

### Connecting Real APIs

Each tool module contains `TODO` comments with code snippets showing exactly how to swap the mock data for a real API or database call:

| Tool | Integration | Setting |
|---|---|---|
| `tools/news_api.py` | NewsAPI.org, GNews, Mediastack | `NEWS_API_KEY` |
| `tools/ais_db.py` | MarineTraffic, VesselFinder | `AIS_API_KEY` |
| `tools/port_db.py` | Internal SQLAlchemy database | `PORT_DB_URL` |
| `tools/weather_api.py` | OpenWeatherMap, StormGlass | `WEATHER_API_KEY` |
| `tools/email_tool.py` | SMTP / SendGrid / Mailgun | `SMTP_*` settings |

### Parallel Agent Execution

The `WorkflowState` nodes in `workflows/daily_report_workflow.py` currently run sequentially. Switch to `asyncio`-based nodes and the LangGraph `Send` API to run all four data-collection agents in parallel.

### Persistent Report Storage

Replace the in-memory `_latest_report` variable in `app/main.py` with a SQLAlchemy model (or object storage like S3) to persist reports across server restarts.

### LLM-Powered Analysis

Add an LLM step inside the `report_agent` (e.g. using `langchain-openai`) to generate natural-language summaries and risk assessments rather than the current template-based output.

### Authentication

Add OAuth2/JWT authentication to the FastAPI endpoints to restrict access to authorised clients.