import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response, status
from fastapi.responses import StreamingResponse

from app.ai import chat
from app.schema.ai import AskIn, AskOut

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])

ThreadId = Annotated[str, Path(min_length=1, max_length=100, pattern=r"\S")]


@router.post("/preguntar", response_model=AskOut)
def preguntar(data: AskIn):
    try:
        return chat.responder(data.pregunta, data.thread_id, data.contexto)
    except Exception:
        logger.exception("Falló el agente")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, chat.ERROR_AGENTE)


@router.post("/preguntar/stream")
def preguntar_stream(data: AskIn):
    return StreamingResponse(
        chat.responder_stream(data.pregunta, data.thread_id, data.contexto),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@router.delete("/conversaciones/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_conversacion(thread_id: ThreadId):
    chat.borrar_conversacion(thread_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
