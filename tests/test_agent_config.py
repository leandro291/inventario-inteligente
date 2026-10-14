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
    assert "[Contexto:" in prompt


def test_historial_resumido():
    assert agent_module.SUMMARY_TRIGGER_TOKENS == 4000
    assert agent_module.SUMMARY_KEEP_MESSAGES == 6
    assert agent_module.agent.checkpointer is not None
