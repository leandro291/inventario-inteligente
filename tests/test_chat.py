import pytest
from langchain_core.messages import AIMessageChunk, ToolMessage

from app.ai import chat
from tests.conftest import parse_sse

MODEL = {"langgraph_node": "model"}


def test_mensaje_usuario_con_y_sin_contexto():
    assert chat.mensaje_usuario("¿Cuáles?", "Pantalla: Productos") == (
        "[Contexto: Pantalla: Productos]\n¿Cuáles?"
    )
    assert chat.mensaje_usuario("¿Cuáles?", None) == "¿Cuáles?"
    assert chat.mensaje_usuario("¿Cuáles?", "") == "¿Cuáles?"


def test_mensaje_usuario_contexto_en_blanco_es_ausente():
    assert chat.mensaje_usuario("¿Cuáles?", "   ") == "¿Cuáles?"
    assert chat.mensaje_usuario("¿Cuáles?", "  Inicio ") == "[Contexto: Inicio]\n¿Cuáles?"


def test_evento_sse():
    assert chat.evento_sse("token", {"texto": "año"}) == 'event: token\ndata: {"texto": "año"}\n\n'


def test_responder(fake_agent, fake_sugerir):
    out = chat.responder("¿Cuántos?", "t1", "Pantalla: Inicio")

    assert out.respuesta == "Hay **3** productos."
    assert out.sugerencias == ["¿Y el stock de Bebidas?"]
    entrada, config = fake_agent.calls[0]
    assert entrada["messages"][0]["content"] == "[Contexto: Pantalla: Inicio]\n¿Cuántos?"
    assert config == {"configurable": {"thread_id": "t1"}}
    assert fake_sugerir.calls == [("¿Cuántos?", "Hay **3** productos.")]


def test_responder_propaga_error_del_agente(fake_agent, fake_sugerir):
    fake_agent.error = RuntimeError("boom")
    with pytest.raises(RuntimeError):
        chat.responder("¿Cuántos?", "t1")


def test_stream_emite_tokens_sugerencias_y_fin(fake_agent, fake_sugerir):
    fake_agent.chunks = [
        (AIMessageChunk(content=""), MODEL),  # chunk de tool call
        (ToolMessage(content="[{'n': 3}]", tool_call_id="1"), {"langgraph_node": "tools"}),
        (AIMessageChunk(content="resumen viejo"), {"langgraph_node": "SummarizationMiddleware.before_model"}),
        (AIMessageChunk(content=[{"type": "text", "text": "x"}]), MODEL),
        (AIMessageChunk(content="Hay "), MODEL),
        (AIMessageChunk(content="**3**"), MODEL),
    ]

    eventos = parse_sse("".join(chat.responder_stream("¿Cuántos?", "t1")))

    assert eventos == [
        ("token", {"texto": "Hay "}),
        ("token", {"texto": "**3**"}),
        ("sugerencias", {"sugerencias": ["¿Y el stock de Bebidas?"]}),
        ("fin", {}),
    ]
    assert fake_sugerir.calls == [("¿Cuántos?", "Hay **3**")]
    assert fake_agent.calls[0][2] == "messages"


def test_stream_separa_mensajes_distintos_del_modelo(fake_agent, fake_sugerir):
    fake_agent.chunks = [
        (AIMessageChunk(content="Voy a ", id="m1"), MODEL),
        (AIMessageChunk(content="mirar.", id="m1"), MODEL),
        (AIMessageChunk(content="Hay 3", id="m2"), MODEL),
    ]

    eventos = parse_sse("".join(chat.responder_stream("¿Cuántos?", "t1")))

    assert [d["texto"] for n, d in eventos if n == "token"] == [
        "Voy a ", "mirar.", "\n\n", "Hay 3",
    ]
    assert fake_sugerir.calls == [("¿Cuántos?", "Voy a mirar.\n\nHay 3")]


def test_stream_error_a_mitad(fake_agent, fake_sugerir):
    fake_agent.chunks = [(AIMessageChunk(content="Hay "), MODEL), RuntimeError("boom")]

    eventos = parse_sse("".join(chat.responder_stream("¿Cuántos?", "t1")))

    assert eventos == [
        ("token", {"texto": "Hay "}),
        ("error", {"detalle": "Falló el agente, intenta de nuevo"}),
    ]
    assert fake_sugerir.calls == []


def test_borrar_conversacion(fake_agent):
    chat.borrar_conversacion("t1")
    assert fake_agent.checkpointer.deleted == ["t1"]


def test_borrar_conversacion_tolera_keyerror(fake_agent):
    def delete_thread(thread_id):
        raise KeyError(thread_id)

    fake_agent.checkpointer.delete_thread = delete_thread
    chat.borrar_conversacion("t1")  # no lanza
