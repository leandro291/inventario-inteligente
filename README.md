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

Al arrancar, `Base.metadata.create_all` crea las tablas si no existen. No migra tablas ya creadas (si cambian las columnas habría que usar Alembic).

## Variables de entorno

| Variable       | Descripción                                      |
|----------------|--------------------------------------------------|
| `DATABASE_URL` | URL de conexión a Postgres (ver `.env.example`)  |

## Estructura

```
main.py            # instancia FastAPI, registra routers, create_all
db.py              # engine, session_local, Base, get_db
dependencies.py    # db_dependency (Annotated[Session, Depends(get_db)])
app/
  models/          # tablas SQLAlchemy (Category, Product)
  schema/          # modelos Pydantic (Base / Create / Update / Out)
  services/        # lógica de acceso a datos (CategoryService, ProductService)
  routers/         # endpoints
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

### Validaciones

- Category: `nombre` 3–100 caracteres.
- Product: `nombre` 3–100, `precio` > 0, `stock` ≥ 0, `category_id` > 0.

## Pendiente / limitaciones conocidas

- Borrar una categoría con productos falla por la FK (500); falta chequeo o `ondelete`.
- `POST /products` con un `category_id` inexistente también falla por la FK.
- Sin `relationship()` entre modelos, sin tests, sin migraciones.
