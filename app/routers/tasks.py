from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.scheduled_task import ScheduledTask
from app.schemas.task import RunNowResponse, TaskCreate, TaskRead, TaskUpdate
from app.services.task_service import create_task, to_task_read, update_task
from app.workers.task_worker import execute_task_run

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_scheduled_task(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskRead:
    try:
        task = create_task(db, payload)
        return to_task_read(task)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{task_id}", response_model=TaskRead)
def get_scheduled_task(task_id: int, db: Session = Depends(get_db)) -> TaskRead:
    task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return to_task_read(task)


@router.patch("/{task_id}", response_model=TaskRead)
def patch_scheduled_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> TaskRead:
    task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        task = update_task(db, task, payload)
        return to_task_read(task)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scheduled_task(task_id: int, db: Session = Depends(get_db)) -> None:
    task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()


@router.post("/{task_id}/run-now", response_model=RunNowResponse)
def run_task_now(task_id: int, db: Session = Depends(get_db)) -> RunNowResponse:
    task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id, ScheduledTask.is_active.is_(True)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_run = execute_task_run(db, task)
    return RunNowResponse(run_id=task_run.id, report_id=task_run.report_id, status=task_run.status)
