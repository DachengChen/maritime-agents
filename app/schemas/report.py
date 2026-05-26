from datetime import datetime

from pydantic import BaseModel


class ReportRead(BaseModel):
    id: int
    task_id: int
    content_markdown: str
    content_html: str
    generated_at: datetime

    model_config = {"from_attributes": True}
