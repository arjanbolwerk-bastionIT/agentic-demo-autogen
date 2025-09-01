
from autogen import AssistantAgent
from orchestrator.model_providers import llm_base

UIUX_SYSTEM = (
    "Je bent UI/UX Designer.
"
    "- Lever IA, belangrijkste schermen en beknopte style guide.
"
    "- Max 200–300 woorden in Markdown."
)

def build_uiux():
    base_url, model, temperature = llm_base("uiux")
    return AssistantAgent(
        name="UIUX",
        system_message=UIUX_SYSTEM,
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
