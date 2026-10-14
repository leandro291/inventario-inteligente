import pytest
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel

from app.ai import agent as agent_module
from app.ai import tools


def test_sin_revisar_sql():
    assert not hasattr(tools, "revisar_sql")
    assert [t.name for t in agent_module.TOOLS] == [
        "listar_tablas",
        "ver_esquema",
        "consultar_sql",
    ]
    assert "revisar_sql" not in agent_module.SYSTEM_PROMPT


def test_prompt_con_reglas_de_formato():
    prompt = agent_module.SYSTEM_PROMPT
    assert "markdown" in prompt.lower()
    assert "$1.234,50" in prompt
    assert "/products?q=" in prompt
    assert "/products?category=" in prompt
    assert "%20" in prompt
    assert "[Contexto:" in prompt


def test_historial_resumido():
    assert agent_module.SUMMARY_TRIGGER_TOKENS == 4000
    assert agent_module.SUMMARY_KEEP_MESSAGES == 6
    assert agent_module.agent.checkpointer is not None


class ModeloQueFalla(BaseChatModel):
    llamadas: int = 0

    @property
    def _llm_type(self):
        return "falla"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.llamadas += 1
        raise RuntimeError("proveedor caído sk-secreto")


def test_reintentos_agotados_propagan_el_error(monkeypatch):
    assert agent_module.MODEL_RETRY.on_failure == "error"
    monkeypatch.setattr("langchain.agents.middleware.model_retry.time.sleep", lambda _: None)
    modelo = ModeloQueFalla()
    agente = create_agent(modelo, [], middleware=[agent_module.MODEL_RETRY])

    with pytest.raises(RuntimeError):
        agente.invoke({"messages": [{"role": "user", "content": "hola"}]})
    assert modelo.llamadas == 4  # 1 intento + 3 reintentos
