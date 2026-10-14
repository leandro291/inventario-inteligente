from langchain_core.messages import AIMessageChunk

from tests.conftest import parse_sse

BODY = {"pregunta": "¿Cuántos productos hay?", "thread_id": "t1"}


def test_preguntar_devuelve_respuesta_y_sugerencias(client):
    r = client.post("/ai/preguntar", json=BODY)
    assert r.status_code == 200
    assert r.json() == {
        "respuesta": "Hay **3** productos.",
        "sugerencias": ["¿Y el stock de Bebidas?"],
    }


def test_preguntar_con_contexto(client, fake_agent):
    client.post("/ai/preguntar", json={**BODY, "contexto": "Pantalla: Productos"})
    entrada, _ = fake_agent.calls[0]
    assert entrada["messages"][0]["content"] == (
        "[Contexto: Pantalla: Productos]\n¿Cuántos productos hay?"
    )


def test_preguntar_sin_thread_id_es_422(client):
    r = client.post("/ai/preguntar", json={"pregunta": "¿Cuántos productos hay?"})
    assert r.status_code == 422


def test_preguntar_contexto_largo_es_422(client):
    r = client.post("/ai/preguntar", json={**BODY, "contexto": "x" * 301})
    assert r.status_code == 422


def test_sugerencias_vacias_no_es_error(client, fake_sugerir):
    fake_sugerir.result = []
    r = client.post("/ai/preguntar", json=BODY)
    assert r.status_code == 200
    assert r.json()["sugerencias"] == []


def test_agente_falla_es_502(client, fake_agent):
    fake_agent.error = RuntimeError("boom")
    r = client.post("/ai/preguntar", json=BODY)
    assert r.status_code == 502
    assert r.json() == {"detail": "Falló el agente, intenta de nuevo"}


def test_stream(client, fake_agent):
    fake_agent.chunks = [(AIMessageChunk(content="Hay 3"), {"langgraph_node": "model"})]
    r = client.post("/ai/preguntar/stream", json=BODY)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    assert r.headers["cache-control"] == "no-cache"
    assert [nombre for nombre, _ in parse_sse(r.text)] == ["token", "sugerencias", "fin"]


def test_stream_422_antes_de_abrir(client):
    r = client.post("/ai/preguntar/stream", json={"pregunta": "¿Cuántos productos hay?"})
    assert r.status_code == 422


def test_borrar_conversacion_idempotente(client, fake_agent):
    assert client.delete("/ai/conversaciones/t1").status_code == 204
    assert client.delete("/ai/conversaciones/t1").status_code == 204
    assert fake_agent.checkpointer.deleted == ["t1", "t1"]


def test_borrar_conversacion_id_largo_es_422(client):
    assert client.delete("/ai/conversaciones/" + "x" * 101).status_code == 422
