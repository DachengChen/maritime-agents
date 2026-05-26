from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.scheduled_task import ScheduleType, ScheduledTask
from app.workers.task_worker import execute_task_run


class SchedulerService:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler(timezone="UTC")

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.add_job(self._poll_and_run_tasks, "interval", minutes=1, id="task-poller", replace_existing=True)
            self.scheduler.start()

    def stop(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def _task_due_now(self, task: ScheduledTask, now_utc: datetime) -> bool:
        local_now = now_utc.astimezone(ZoneInfo(task.timezone))
        hhmm = local_now.strftime("%H:%M")
        if hhmm != task.schedule_time:
            return False

        if task.schedule_type == ScheduleType.WEEKLY.value and local_now.weekday() != task.schedule_day_of_week:
            return False

        if task.last_run_at is not None:
            last_local = task.last_run_at.astimezone(ZoneInfo(task.timezone))
            if task.schedule_type == ScheduleType.DAILY.value and last_local.date() == local_now.date():
                return False
            if task.schedule_type == ScheduleType.WEEKLY.value and last_local.isocalendar()[:2] == local_now.isocalendar()[:2]:
                return False

        return True

    def _poll_and_run_tasks(self) -> None:
        now_utc = datetime.now(UTC).replace(second=0, microsecond=0)
        db: Session = SessionLocal()
        try:
            tasks = db.query(ScheduledTask).filter(ScheduledTask.is_active.is_(True)).all()
            for task in tasks:
                if self._task_due_now(task, now_utc):
                    execute_task_run(db, task)
        finally:
            db.close()


scheduler_service = SchedulerService()
