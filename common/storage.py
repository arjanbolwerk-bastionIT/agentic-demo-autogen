
import os
from sqlmodel import SQLModel, create_engine, Session, select
from .events import AgentEvent

DB_URL = os.getenv("DB_URL", "sqlite:////workspace/artifacts/events.db")
engine = create_engine(DB_URL, echo=False)
SQLModel.metadata.create_all(engine)

def add_event(**kwargs):
    with Session(engine) as s:
        ev = AgentEvent(**kwargs)
        s.add(ev)
        s.commit()

def get_events(run_id: str):
    with Session(engine) as s:
        stmt = select(AgentEvent).where(AgentEvent.run_id == run_id).order_by(AgentEvent.ts)
        return list(s.exec(stmt))
