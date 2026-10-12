# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Estado del proyecto

Esqueleto inicial: sin commits, sin README, sin tests, sin linter configurado. `main.py`, `db.py` y `dependencies.py` (raíz) están vacíos, y `app/{models,routers,schema,services}/` son carpetas vacías. Actualizar este archivo cuando haya código real.

## Stack

FastAPI (+ pydantic v2, pydantic-settings, python-dotenv), uvicorn. ORM: SQLAlchemy 2.0 (estilo 2.0: `DeclarativeBase`, `Mapped[]`/`mapped_column`, `select()`), todavía no está en `requirements.txt` ni hay driver de DB; agregarlos al implementar `db.py`. Las dependencias están fijadas en `requirements.txt` (salida de `pip freeze`, incluye extras como opentelemetry/sentry-sdk que el código aún no usa).

## Comandos

```bash
source venv/bin/activate          # venv local, ignorado por git
pip install -r requirements.txt
fastapi dev main.py               # servidor de desarrollo (fastapi-cli instalado); requiere que main.py defina `app`
```

Config sensible va en `.env` (ignorado por git).

## Estructura prevista

Layout por capas, a partir de los nombres de carpetas:

- `main.py` — instancia `FastAPI` y registra routers
- `db.py` — conexión/sesión de base de datos
- `dependencies.py` — dependencias compartidas de FastAPI (`Depends`)
- `app/routers/` — endpoints
- `app/schema/` — modelos pydantic (request/response)
- `app/models/` — modelos de persistencia
- `app/services/` — lógica de negocio
