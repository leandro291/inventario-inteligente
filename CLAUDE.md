# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Estado del proyecto

Esqueleto inicial: sin commits, sin README, sin tests, sin linter configurado. `main.py`, `db.py` y `dependencies.py` (raíz) están vacíos, y `app/{models,routers,schema,services}/` son carpetas vacías. Actualizar este archivo cuando haya código real.

## Stack

FastAPI (+ pydantic v2, pydantic-settings, python-dotenv), uvicorn. ORM: SQLAlchemy 2.0 (estilo 2.0: `DeclarativeBase`, `Mapped[]`/`mapped_column`, `select()`), en `requirements.txt` (v2.0.54); DB: Postgres (Neon) vía `DATABASE_URL` en `.env`, driver psycopg2-binary. Las dependencias están fijadas en `requirements.txt` (salida de `pip freeze`, incluye extras como opentelemetry/sentry-sdk que el código aún no usa).

## Comandos

```bash
source venv/bin/activate          # venv local, ignorado por git
pip install -r requirements.txt
fastapi dev main.py               # servidor de desarrollo (fastapi-cli instalado); o `uvicorn main:app --reload`
```

Migraciones (Alembic, config en `migrations/env.py`, URL desde `db.py`): `alembic revision --autogenerate -m "msg"` y `alembic upgrade head`. La app no llama `create_all`; todo cambio de esquema pasa por una migración.

Config sensible va en `.env` (ignorado por git).

## Estructura prevista

Layout por capas, a partir de los nombres de carpetas:

- `main.py` — instancia `FastAPI` y registra routers (no crea tablas: eso es Alembic)
- `db.py` — conexión/sesión de base de datos
- `dependencies.py` — dependencias compartidas de FastAPI (`Depends`)
- `app/routers/` — endpoints
- `app/schema/` — modelos pydantic (request/response)
- `app/models/` — modelos de persistencia
- `app/services/` — lógica de negocio

## Modelo de datos

Ejemplo para practicar (categorías y productos). Fuente de verdad del ERM:

@ERM.md
