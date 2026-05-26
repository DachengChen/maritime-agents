from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.agents.report_agent import report_agent
from app.models.report import Report
from app.models.scheduled_task import ScheduledTask
from app.models.task_run import TaskRun, TaskRunStatus
from app.services.email_service import email_service


def execute_task_run(db: Session, task: ScheduledTask) -> TaskRun:
    """Execute one report generation pipeline for a scheduled task.

    TODO: Move execution to Celery/RQ workers for horizontal scaling.
    """

    task_run = TaskRun(task_id=task.id, status=TaskRunStatus.RUNNING.value)
    db.add(task_run)
    db.commit()
    db.refresh(task_run)

    try:
        markdown = report_agent.generate_report(task.requirement_text, task.preferred_report_language)
        html = email_service.render_report_html(markdown, task.requirement_text)
        report = Report(task_id=task.id, content_markdown=markdown, content_html=html)
        db.add(report)
        db.commit()
        db.refresh(report)

        email_service.send_report_email(
            recipient_email=task.user.email,
            subject=f"Maritime Intelligence Report - Task #{task.id}",
            markdown_content=markdown,
            html_content=html,
        )

        task.last_run_at = datetime.now(UTC)
        task_run.status = TaskRunStatus.SUCCESS.value
        task_run.report_id = report.id
        task_run.ended_at = datetime.now(UTC)
        db.commit()
        db.refresh(task_run)
        return task_run
    except Exception as exc:
        task_run.status = TaskRunStatus.FAILED.value
        task_run.error_message = str(exc)
        task_run.ended_at = datetime.now(UTC)
        db.commit()
        db.refresh(task_run)
        return task_run
