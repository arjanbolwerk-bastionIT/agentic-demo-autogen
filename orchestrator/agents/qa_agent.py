
from autogen import AssistantAgent
from orchestrator.model_providers import llm_base

QA_SYSTEM = (
    "Je bent QA Engineer.
"
    "- Beschrijf teststrategie en prioritaire testgevallen.
"
    "- Koppel aan ReqIDs. Max 150–250 woorden in Markdown."
)

def build_qa():
    base_url, model, temperature = llm_base("qa")
    return AssistantAgent(
        name="QA",
        system_message=QA_SYSTEM,
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
