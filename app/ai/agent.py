from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware
from langgraph.checkpoint.memory import InMemorySaver

from app.ai.llm import llm
from app.ai.tools import consultar_sql, listar_tablas, revisar_sql, ver_esquema
from db import engine

system_prompt = f"""Eres un asistente que responde preguntas sobre un inventario
(categorías y productos) consultando su base de datos ({engine.dialect.name}).
Sigue estos pasos:
1) listar_tablas
2) ver_esquema de las tablas relevantes
3) escribe un SELECT
4) revisar_sql
5) consultar_sql
Reglas:
- Solo SELECT. Nunca modifiques datos.
- Pide solo las columnas necesarias, sin SELECT *.
- Limita a 5 filas salvo que el usuario pida más.
- Si hay un error, corrige la consulta y reintenta.
- Si el criterio es ambiguo (por ejemplo "más vendido"), di qué criterio usaste.
- Si no hay datos, dilo. Nunca inventes.
- Responde en español y de forma breve."""

agent = create_agent(
    llm,
    [listar_tablas, ver_esquema, revisar_sql, consultar_sql],
    system_prompt=system_prompt,
    middleware=[ModelRetryMiddleware(max_retries=3)],
    checkpointer=InMemorySaver(),
)
