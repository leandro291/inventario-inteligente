# CLAUDE.md

Back de Inventario Inteligente: FastAPI + pydantic v2, SQLAlchemy 2.0 (`DeclarativeBase`, `Mapped[]`/`mapped_column`, `select()`), Postgres en Neon vía `DATABASE_URL` en `.env` (psycopg2-binary). Agente SQL con LangChain en `app/ai/`.

## Comandos

```bash
source venv/bin/activate
pip install -r requirements.txt
fastapi dev main.py
alembic revision --autogenerate -m "msg"
alembic upgrade head
```

`main.py` crea las tablas que faltan con `create_all` al arrancar; todo cambio sobre tablas existentes pasa por una migración Alembic (config en `migrations/env.py`, URL desde `db.py`). Config sensible solo en `.env`.

## Estructura

`main.py` (app + routers) · `db.py` (engine/sesión) · `dependencies.py` (`Depends`) · `app/routers/` endpoints · `app/schema/` pydantic · `app/models/` SQLAlchemy · `app/services/` lógica · `app/ai/` agente.

## Modelo de datos

@ERM.md
