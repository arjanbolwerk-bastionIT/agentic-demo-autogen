import os, json, time, subprocess
from autogen import UserProxyAgent
from orchestrator.agents.ba_agent import build_ba
from orchestrator.agents.uiux_agent import build_uiux
from orchestrator.agents.dev_agent import build_dev
from orchestrator.agents.qa_agent import build_qa
from common.storage import add_event
from github_client import ensure_repo_sync, commit_and_push, create_or_update_pr

WORKSPACE_APP = "/workspace/app"
REPORT_DIR = "/workspace/artifacts/reports"
REPORT_PATH = f"{REPORT_DIR}/test_report.md"
PENDING_DIR = "/workspace/artifacts/pending"

os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(PENDING_DIR, exist_ok=True)
os.makedirs(WORKSPACE_APP, exist_ok=True)

def log(run_id, agent, phase, content):
    add_event(run_id=run_id, agent=agent, phase=phase, content=content)

def run_pytests():
    try:
        out = subprocess.run(
            ["pytest", "-q"],
            cwd=WORKSPACE_APP,
            capture_output=True,
            text=True,
            timeout=300
        )
        stdout = out.stdout or ""
        stderr = out.stderr or ""
        return out.returncode, stdout + "\n" + stderr
    except Exception as e:
        return 99, str(e)

def _reply_text(agent, messages):
    """Robuuste wrapper: 1 beurt genereren, return altijd string."""
    try:
        rep = agent.generate_reply(messages=messages)
        if isinstance(rep, str):
            return rep
        if isinstance(rep, dict) and "content" in rep:
            return rep["content"]
        if isinstance(rep, list) and rep and isinstance(rep[0], dict) and "content" in rep[0]:
            return rep[0]["content"]
        return str(rep)
    except Exception as e:
        return f"(agent reply failed: {e})"

def process_job(job):
    run_id = job["run_id"]
    req_text = job["requirements"]

    log(run_id, "WORKFLOW", "start", "Run gestart.")
    try:
        ensure_repo_sync()
        log(run_id, "WORKFLOW", "output", "ensure_repo_sync OK")
    except Exception as e:
        log(run_id, "WORKFLOW", "error", f"Repo sync faalde: {e}")
        return

    # Build agents (géén GroupChat; sequentieel 1 beurt per stap)
    user = UserProxyAgent(name="USER")
    ba, uiux, dev, qa = build_ba(), build_uiux(), build_dev(), build_qa()

    # ===== BA =====
    log(run_id, "BA", "start", "BA analyse start...")
    log(run_id, "BA", "input", f"Invoer ({len(req_text)} chars)")
    ba_text = _reply_text(ba, messages=[
        {"role": "system", "content": ba.system_message},
        {"role": "user",   "content": req_text},
    ])
    preview = (ba_text or "")[:200].replace("\n", " ")
    log(run_id, "BA", "output", f"BA OK (preview): {preview}...")
    try:
        with open("/workspace/artifacts/ba_spec.md", "w", encoding="utf-8") as f:
            f.write(ba_text)
    except Exception:
        pass
    log(run_id, "BA", "done", "BA gereed.")

    # ===== UI/UX =====
    log(run_id, "UIUX", "start", "UI/UX start...")
    log(run_id, "UIUX", "input", "BA output als basis.")
    uiux_text = _reply_text(uiux, messages=[
        {"role": "system", "content": uiux.system_message},
        {"role": "user",   "content": ba_text},
    ])
    try:
        os.makedirs("/workspace/app", exist_ok=True)
        with open("/workspace/app/README.uiux.md", "w", encoding="utf-8") as f:
            f.write(uiux_text)
    except Exception:
        pass
    log(run_id, "UIUX", "output", "UI/UX artefact: /workspace/app/README.uiux.md")
    log(run_id, "UIUX", "done", "UI/UX gereed.")

    # ===== DEV =====
    log(run_id, "DEV", "start", "Dev implementatie start...")
    log(run_id, "DEV", "input", "BA + UI/UX artefact.")
    dev_text = _reply_text(dev, messages=[
        {"role": "system", "content": dev.system_message},
        {"role": "user",   "content": f"BA:\n{ba_text}\n\nUI/UX:\n{uiux_text}"},
    ])
    try:
        os.makedirs("/workspace/app/backend", exist_ok=True)
        with open("/workspace/app/backend/app.py", "w", encoding="utf-8") as f:
            f.write(
                "from fastapi import FastAPI\n"
                "app = FastAPI()\n"
                "@app.get('/health')\n"
                "def health():\n"
                "    return {'ok': True}\n"
            )
        with open("/workspace/app/README.dev.md", "w", encoding="utf-8") as f:
            f.write(dev_text)
    except Exception:
        pass
    log(run_id, "DEV", "output", "Dev artefacten: backend/app.py, README.dev.md")
    log(run_id, "DEV", "done", "Dev gereed.")

    # ===== QA =====
    log(run_id, "QA", "start", "QA start tests...")
    log(run_id, "QA", "input", "Run pytest over /workspace/app.")
    code, test_output = run_pytests()
    try:
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write("## Pytest Resultaat (exit {})\n```\n{}\n```".format(code, test_output))
    except Exception:
        pass
    log(run_id, "QA", "output", f"pytest exit={code}; rapport: artifacts/reports/test_report.md")

    # ===== Finish =====
    try:
        commit_and_push(message=f"Run {run_id}: implementatie + rapporten")
        pr_url = create_or_update_pr(title=f"Run {run_id}", body="Automatische PR door agents.")
    except Exception as e:
        pr_url = f"(PR aanmaken faalde: {e})"
    log(run_id, "WORKFLOW", "done", f"PR/Issue: {pr_url}")

def main_loop():
    print("[loop] started", flush=True)
    while True:
        try:
            files = [f for f in os.listdir(PENDING_DIR) if f.endswith(".json")]
            if files:
                print("[loop] pending:", files, flush=True)
            for name in files:
                path = os.path.join(PENDING_DIR, name)
                with open(path, "r", encoding="utf-8") as f:
                    job = json.load(f)
                try:
                    os.remove(path)
                except Exception as e:
                    print("[loop] warn: could not remove", name, e, flush=True)
                print("[loop] processing run_id:", job.get("run_id"), flush=True)
                process_job(job)
            time.sleep(1)
        except Exception as e:
            print("[loop] error:", e, flush=True)
            time.sleep(2)

if __name__ == "__main__":
    main_loop()
