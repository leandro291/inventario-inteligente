
from app.ai.llm import llm
from app.schema.ai import Sugerencias

MAX_SUGERENCIAS = 3

PROMPT = """Un usuario le preguntó a un asistente de inventario (productos, categorías y stock):
{pregunta}

El asistente respondió:
{respuesta}

Propón hasta 3 preguntas de seguimiento que el usuario podría hacer a continuación.
Reglas: en español, cortas (máximo 80 caracteres), que se puedan responder con
datos de productos, categorías y stock, y distintas de la pregunta original."""


modelo_sugerencias = llm.with_structured_output(Sugerencias)


def sugerir(pregunta: str, respuesta: str) -> list[str]:
    """Hasta 3 preguntas de seguimiento. Nunca falla: ante un error devuelve []."""
    try:
        resultado = modelo_sugerencias.invoke(
            PROMPT.format(pregunta=pregunta, respuesta=respuesta)
        )
    except Exception:
        return []
    if resultado is None:
        return []
    original = pregunta.strip().lower()
    vistas: list[str] = []
    for texto in (s.strip() for s in resultado.sugerencias):
        if texto and texto not in vistas and texto.lower() != original:
            vistas.append(texto)
    return vistas[:MAX_SUGERENCIAS]
