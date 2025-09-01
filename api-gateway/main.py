
from fastapi import FastAPI
from pydantic import BaseModel
import os, json, uuid
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session, select
from common.events import AgentEvent
from fastapi.responses import PlainTextResponse

app = FastAPI(title="Agentic Devline API")
DB_URL = os.getenv("DB_URL", "sqlite:////workspace/artifacts/events.db")
engine = create_engine(DB_URL, echo=False)
SQLModel.metadata.create_all(engine)

class NewRun(BaseModel):
    project_name: str
    requirements: str
    non_functionals: str | None = None
    tech_prefs: str | None = None

@app.post("/runs")
def start_run(r: NewRun):
    run_id = str(uuid.uuid4())
    nf = r.non_functionals or ""; tp = r.tech_prefs or ""
    req_text = (
        f"# Project: {r.project_name}

"
        f"{r.requirements}

"
        f"Non-functionals:
{nf}
"
        f"Tech:
{tp}"
    )
    payload = {"run_id": run_id, "requirements": req_text}
    pending = Path("/workspace/artifacts/pending"); pending.mkdir(parents=True, exist_ok=True)
    with open(pending / "run.json", "w", encoding="utf-8") as f:
        json.dump(payload, f)
    return {"run_id": run_id}

@app.get("/runs/{run_id}/events")
def get_events(run_id: str):
    with Session(engine) as s:
        stmt = select(AgentEvent).where(AgentEvent.run_id == run_id).order_by(AgentEvent.ts)
        rows = s.exec(stmt)
        return [{
            "id": e.id, "run_id": e.run_id, "agent": e.agent,
            "phase": e.phase, "content": e.content, "ts": e.ts.isoformat()
        } for e in rows]

REPORT_PATH = "/workspace/artifacts/reports/test_report.md"

@app.get("/runs/{run_id}/report", response_class=PlainTextResponse)
def get_report(run_id: str):
    try:
        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Nog geen rapport beschikbaar."
