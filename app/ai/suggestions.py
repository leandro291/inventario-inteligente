import logging

from pydantic import BaseModel

from app.ai.llm import llm

MAX_SUGERENCIAS = 3

logger = logging.getLogger(__name__)

PROMPT = """Un usuario le preguntó a un asistente de inventario (productos, categorías y stock):
{pregunta}

El asistente respondió:
{respuesta}

Propón hasta 3 preguntas de seguimiento que el usuario podría hacer a continuación.
Reglas: en español, cortas (máximo 80 caracteres), que se puedan responder con
datos de productos, categorías y stock, y distintas de la pregunta original."""


class Sugerencias(BaseModel):
    sugerencias: list[str]


modelo_sugerencias = llm.with_structured_output(Sugerencias)


def sugerir(pregunta: str, respuesta: str) -> list[str]:
    """Hasta 3 preguntas de seguimiento. Nunca falla: ante un error devuelve []."""
    try:
        resultado = modelo_sugerencias.invoke(
            PROMPT.format(pregunta=pregunta, respuesta=respuesta)
        )
    except Exception:
        logger.exception("No se pudieron generar sugerencias")
        return []
    if resultado is None:
        return []
    original = pregunta.strip().lower()
    vistas: list[str] = []
    for texto in (s.strip() for s in resultado.sugerencias):
        if texto and texto not in vistas and texto.lower() != original:
            vistas.append(texto)
    return vistas[:MAX_SUGERENCIAS]
