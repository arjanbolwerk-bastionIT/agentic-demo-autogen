
from autogen import AssistantAgent
from orchestrator.model_providers import llm_base

DEV_SYSTEM = (
    "Je bent Senior Developer.
"
    "- Beschrijf een minimalistische backend-skeleton (FastAPI /health) en test-aanpak.
"
    "- Max 150–250 woorden in Markdown."
)

def build_dev():
    base_url, model, temperature = llm_base("dev")
    return AssistantAgent(
        name="DEV",
        system_message=DEV_SYSTEM,
        llm_config={
            "config_list": [{
                "api_type": "openai",
                "model": model,
                "api_base": f"{base_url}/v1",
                "api_key": "ollama",
            }],
            "temperature": temperature,
            "timeout": 120,
            "stream": False,
        },
    )
