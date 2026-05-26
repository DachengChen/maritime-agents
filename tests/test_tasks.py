from unittest.mock import patch

from app.agents.report_agent import report_agent


def create_task_payload() -> dict:
    return {
        "email": "ops@example.com",
        "requirement_text": "Monitor vessel congestion and weather risk in Asia ports",
        "schedule": "daily 07:00",
        "timezone": "UTC",
        "preferred_report_language": "en",
    }


def test_create_task(client):
    response = client.post("/tasks", json=create_task_payload())
    assert response.status_code == 201
    data = response.json()
    assert data["user_email"] == "ops@example.com"
    assert data["schedule_type"] == "daily"
    assert data["schedule_time"] == "07:00"


def test_run_task_manually_and_get_latest_report(client):
    create_response = client.post("/tasks", json=create_task_payload())
    task_id = create_response.json()["id"]

    run_response = client.post(f"/tasks/{task_id}/run-now")
    assert run_response.status_code == 200
    assert run_response.json()["status"] == "success"

    latest_report = client.get(f"/reports/{task_id}/latest")
    assert latest_report.status_code == 200
    assert "Maritime Intelligence Report" in latest_report.json()["content_markdown"]


def test_report_generation_direct():
    report = report_agent.generate_report("Track weather and vessel movement", language="en")
    assert "Weather Outlook" in report
    assert "Vessel Movements" in report


def test_email_send_is_mocked(client):
    create_response = client.post("/tasks", json=create_task_payload())
    task_id = create_response.json()["id"]

    with patch("app.services.email_service.EmailService.send_report_email") as mocked_send:
        run_response = client.post(f"/tasks/{task_id}/run-now")

    assert run_response.status_code == 200
    mocked_send.assert_called_once()
