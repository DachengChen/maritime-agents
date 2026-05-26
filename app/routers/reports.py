from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.report import Report
from app.schemas.report import ReportRead

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{task_id}/latest", response_model=ReportRead)
def get_latest_report(task_id: int, db: Session = Depends(get_db)) -> ReportRead:
    report = (
        db.query(Report)
        .filter(Report.task_id == task_id)
        .order_by(Report.generated_at.desc(), Report.id.desc())
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="No report found for task")
    return ReportRead.model_validate(report)
