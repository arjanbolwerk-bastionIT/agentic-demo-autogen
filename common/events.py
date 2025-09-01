
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class AgentEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: str
    agent: str
    phase: str
    content: str
    ts: datetime = Field(default_factory=datetime.utcnow)
