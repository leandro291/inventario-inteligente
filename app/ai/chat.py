import json
import logging
from collections.abc import Iterator

from langchain_core.messages import AIMessageChunk

from app.ai.agent import agent
from app.ai.suggestions import sugerir
from app.schema.ai import AskOut

ERROR_AGENTE = "Falló el agente, intenta de nuevo"

logger = logging.getLogger(__name__)


def mensaje_usuario(pregunta: str, contexto: str | None) -> str:
    contexto = (contexto or "").strip()
    return f"[Contexto: {contexto}]\n{pregunta}" if contexto else pregunta


def _entrada(pregunta: str, contexto: str | None) -> dict:
    return {"messages": [{"role": "user", "content": mensaje_usuario(pregunta, contexto)}]}


def _config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def evento_sse(nombre: str, data: dict) -> str:
    return f"event: {nombre}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def responder(pregunta: str, thread_id: str, contexto: str | None = None) -> AskOut:
    """Respuesta completa + sugerencias. Los errores del agente se propagan."""
    resultado = agent.invoke(_entrada(pregunta, contexto), config=_config(thread_id))
    respuesta = resultado["messages"][-1].content
    return AskOut(respuesta=respuesta, sugerencias=sugerir(pregunta, respuesta))


def responder_stream(
    pregunta: str, thread_id: str, contexto: str | None = None
) -> Iterator[str]:
    """Eventos SSE: token... → sugerencias → fin, o error si el agente falla."""
    # ponytail: si ModelRetryMiddleware reintenta tras emitir tokens, los del intento
    # fallido quedan en el stream. Upgrade: evento "reinicio" al detectar un chunk.id
    # nuevo sin tool_call_chunks.
    partes: list[str] = []
    ultimo_id = None
    try:
        for chunk, metadata in agent.stream(
            _entrada(pregunta, contexto),
            config=_config(thread_id),
            stream_mode="messages",
        ):
            # Solo texto del modelo principal: ni tools ni el modelo de resumen
            if metadata.get("langgraph_node") != "model":
                continue
            if not isinstance(chunk, AIMessageChunk):
                continue
            if not isinstance(chunk.content, str) or not chunk.content:
                continue
            # Otro mensaje del modelo (p. ej. tras una tool): separa los párrafos
            if partes and chunk.id != ultimo_id:
                partes.append("\n\n")
                yield evento_sse("token", {"texto": "\n\n"})
            ultimo_id = chunk.id
            partes.append(chunk.content)
            yield evento_sse("token", {"texto": chunk.content})
    except Exception:
        logger.exception("Falló el agente durante el streaming")
        yield evento_sse("error", {"detalle": ERROR_AGENTE})
        return
    yield evento_sse("sugerencias", {"sugerencias": sugerir(pregunta, "".join(partes))})
    yield evento_sse("fin", {})


def borrar_conversacion(thread_id: str) -> None:
    try:
        agent.checkpointer.delete_thread(thread_id)
    except KeyError:  # InMemorySaver no es atómico: doble borrado concurrente
        pass
