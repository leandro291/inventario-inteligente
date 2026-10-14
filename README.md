# Inventario Inteligente

API REST de ejemplo para practicar FastAPI con SQLAlchemy 2.0: gestión de **categorías** y **productos**.

## Stack

- FastAPI + Pydantic v2
- SQLAlchemy 2.0 (`DeclarativeBase`, `Mapped`, `mapped_column`)
- PostgreSQL (Neon) con `psycopg2-binary`
- uvicorn, python-dotenv

## Puesta en marcha

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # y completar DATABASE_URL
uvicorn main:app --reload   # o: fastapi dev main.py
```

Docs interactivas: http://127.0.0.1:8000/docs

### Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Los tests no usan red: reemplazan el agente y el LLM por fakes y no tocan la base.

Al arrancar, `main.py` crea las tablas que faltan con `Base.metadata.create_all`. Los cambios sobre tablas existentes (columnas, constraints) van por Alembic (ver [Migraciones](#migraciones)).

## Variables de entorno

| Variable       | Descripción                                      |
|----------------|--------------------------------------------------|
| `DATABASE_URL` | URL de conexión a Postgres (ver `.env.example`)  |

## Estructura

```
main.py            # instancia FastAPI y registro de routers
db.py              # engine, session_local, Base, get_db
dependencies.py    # db_dependency (Annotated[Session, Depends(get_db)])
app/
  models/          # tablas SQLAlchemy (Category, Product)
  schema/          # modelos Pydantic (Base / Create / Update / Out)
  services/        # lógica de acceso a datos (CategoryService, ProductService)
  routers/         # endpoints
migrations/        # Alembic (versions/ = historial de cambios del esquema)
alembic.ini
```

Flujo de una request: `router` → `service` (recibe la `Session`) → `model`; la respuesta se serializa con el schema `Out`.

## Modelo de datos

Ver [ERM.md](ERM.md). Resumen: `categories (id, nombre)` 1—N `products (id, nombre, precio, stock, category_id)`.

## Endpoints

Mismos cinco endpoints para `/categories` y `/products`:

| Método | Ruta     | Descripción        | Respuesta |
|--------|----------|--------------------|-----------|
| GET    | `/`      | Listar             | 200       |
| GET    | `/{id}`  | Obtener por id     | 200 / 404 |
| POST   | `/`      | Crear              | 201       |
| PATCH  | `/{id}`  | Actualizar parcial | 200 / 404 |
| DELETE | `/{id}`  | Borrar (físico)    | 204 / 404 |

### Chat IA

- `POST /ai/preguntar` — body `{pregunta: 3–500, thread_id: 1–100 (obligatorio), contexto?: ≤300}` → `{respuesta, sugerencias: string[]}`. `502` si falla el agente.
- `POST /ai/preguntar/stream` — mismo body; responde `text/event-stream` con eventos `token` (`{texto}`), `sugerencias` (`{sugerencias}`), `fin` (`{}`) o `error` (`{detalle}`).
- `DELETE /ai/conversaciones/{thread_id}` — `204`; borra la memoria de esa conversación (idempotente).

La memoria vive en RAM (`InMemorySaver`): se pierde al reiniciar el servidor. Las conversaciones largas se resumen solas.

### Validaciones

- Category: `nombre` 3–100 caracteres.
- Product: `nombre` 3–100, `precio` > 0, `stock` ≥ 0, `category_id` > 0.

## Migraciones

Alembic lee la URL desde `db.py` (`.env`), no desde `alembic.ini`.

```bash
alembic revision --autogenerate -m "descripción"   # tras cambiar un modelo; revisar el archivo generado
alembic upgrade head                                # aplicar
alembic downgrade -1                                # deshacer el último
alembic current                                     # revisión actual de la base
```

Autogenerate no detecta renombres de columna: revisar siempre el archivo antes de aplicar.

## Pendiente

- Borrar una categoría con productos, o crear/actualizar un producto con `category_id` inexistente, falla por la FK (500).
- Sin `relationship()` entre modelos.
