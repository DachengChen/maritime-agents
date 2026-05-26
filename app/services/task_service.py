from sqlalchemy.orm import Session

from app.models.scheduled_task import ScheduledTask
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.schedule_parser import parse_schedule


def get_or_create_user(db: Session, email: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def to_task_read(task: ScheduledTask) -> TaskRead:
    return TaskRead(
        id=task.id,
        user_email=task.user.email,
        requirement_text=task.requirement_text,
        schedule_type=task.schedule_type,
        schedule_time=task.schedule_time,
        schedule_day_of_week=task.schedule_day_of_week,
        timezone=task.timezone,
        preferred_report_language=task.preferred_report_language,
        is_active=task.is_active,
        last_run_at=task.last_run_at,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def create_task(db: Session, payload: TaskCreate) -> ScheduledTask:
    user = get_or_create_user(db, payload.email)
    parsed_schedule = parse_schedule(payload.schedule)

    task = ScheduledTask(
        user_id=user.id,
        requirement_text=payload.requirement_text,
        schedule_type=parsed_schedule.schedule_type,
        schedule_time=parsed_schedule.schedule_time,
        schedule_day_of_week=parsed_schedule.schedule_day_of_week,
        timezone=payload.timezone,
        preferred_report_language=payload.preferred_report_language,
        is_active=True,
    )

    db.add(task)
    db.commit()
    db.refresh(task)
    db.refresh(user)
    return task


def update_task(db: Session, task: ScheduledTask, payload: TaskUpdate) -> ScheduledTask:
    if payload.requirement_text is not None:
        task.requirement_text = payload.requirement_text
    if payload.timezone is not None:
        task.timezone = payload.timezone
    if payload.preferred_report_language is not None:
        task.preferred_report_language = payload.preferred_report_language
    if payload.is_active is not None:
        task.is_active = payload.is_active

    if payload.schedule is not None:
        parsed_schedule = parse_schedule(payload.schedule)
        task.schedule_type = parsed_schedule.schedule_type
        task.schedule_time = parsed_schedule.schedule_time
        task.schedule_day_of_week = parsed_schedule.schedule_day_of_week

    db.commit()
    db.refresh(task)
    return task
