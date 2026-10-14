from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware, SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver

from app.ai.llm import llm
from app.ai.tools import consultar_sql, listar_tablas, ver_esquema
from db import engine

TOOLS = [listar_tablas, ver_esquema, consultar_sql]

# Al pasar el umbral, resume lo viejo y conserva los últimos mensajes
SUMMARY_TRIGGER_TOKENS = 4000
SUMMARY_KEEP_MESSAGES = 6

SYSTEM_PROMPT = f"""Eres un asistente que responde preguntas sobre un inventario
(categorías y productos) consultando su base de datos ({engine.dialect.name}).
Sigue estos pasos:
1) listar_tablas
2) ver_esquema de las tablas relevantes
3) escribe un SELECT
4) consultar_sql
Reglas:
- Solo SELECT. Nunca modifiques datos.
- Pide solo las columnas necesarias, sin SELECT *.
- Limita a 5 filas salvo que el usuario pida más.
- Si hay un error, corrige la consulta y reintenta.
- Si el criterio es ambiguo (por ejemplo "más vendido"), di qué criterio usaste.
- Si no hay datos, dilo. Nunca inventes.
- Responde en español y de forma breve.
Formato de la respuesta (se muestra como markdown):
- Usa listas para enumerar; usa una tabla solo para comparar 3 o más filas con varias columnas.
- Pon en **negrita** el dato clave.
- Montos con formato argentino: $1.234,50. Cantidades con punto de miles: 1.250.
- Al nombrar un producto, enlázalo así: [nombre](/products?q=nombre).
  Los espacios del enlace van como %20: [Coca Cola](/products?q=Coca%20Cola).
  Al nombrar una categoría: [nombre](/products?category=id).
  Usa solo esas rutas; nunca enlaces externos.
- Si la pregunta empieza con [Contexto: ...], úsalo para interpretar referencias
  como "estos" o "esta categoría"."""

# on_failure="error": agotados los reintentos se propaga la excepción (el default
# "continue" devolvería el error del proveedor como si fuera la respuesta)
MODEL_RETRY = ModelRetryMiddleware(max_retries=3, on_failure="error")

agent = create_agent(
    llm,
    TOOLS,
    system_prompt=SYSTEM_PROMPT,
    middleware=[
        SummarizationMiddleware(
            llm,
            trigger=("tokens", SUMMARY_TRIGGER_TOKENS),
            keep=("messages", SUMMARY_KEEP_MESSAGES),
        ),
        MODEL_RETRY,
    ],
    checkpointer=InMemorySaver(),
)
