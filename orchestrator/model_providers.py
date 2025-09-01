
import os

def llm_base(role: str):
    base = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    model = os.getenv("GEN_MODEL", "qwen2.5:3b")
    # You can tune temperature per role if you want
    temps = {"ba":0.3, "uiux":0.3, "dev":0.2, "qa":0.2}
    return base, model, temps.get(role, 0.3)
