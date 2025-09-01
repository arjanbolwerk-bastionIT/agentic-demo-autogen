
from autogen import AssistantAgent
from orchestrator.model_providers import llm_base

BA_SYSTEM = (
    "Je bent een Business Analyst.
"
    "- Analyseer de gebruikersvereisten.
"
    "- Lever doel, scope, 3–7 user stories (met ID) en non-functionals.
"
    "- Voeg compacte traceability (ReqID -> Stories -> Testcases) toe.
"
    "- Max 200–300 woorden in Markdown."
)

def build_ba():
    base_url, model, temperature = llm_base("ba")
    return AssistantAgent(
        name="BA",
        system_message=BA_SYSTEM,
        llm_config={
            "config_list": [{
                "api_type": "openai",
                "model": model,
                "api_base": f"{base_url}/v1",
                "api_key": "ollama",
            }],
            "temperature": temperature,
            "timeout": 180,
            "stream": False,
        },
    )
