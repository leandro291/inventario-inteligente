import re

from langchain.tools import tool
from sqlalchemy import inspect, text

from app.ai.llm import llm
from db import engine

TABLAS_PERMITIDAS = {"categories", "products"}
MAX_FILAS = 50
TIMEOUT_MS = 5000

PROHIBIDAS = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|copy|call|do)\b",
    re.I,
)


def validar(sql: str) -> str | None:
    """Devuelve un mensaje de error o None si es válida."""
    s = sql.strip().rstrip(";")
    if not re.match(r"(?is)^\s*select\b", s):
        return "Error: solo se permite un SELECT."
    if ";" in s:
        return "Error: solo una consulta a la vez."
    if PROHIBIDAS.search(s):
        return "Error: operación no permitida."
    # ponytail: heurística por regex; falla con EXTRACT(x FROM col) (falso rechazo).
    # Para algo más fino, parsear con sqlglot.
    usadas = {
        t.strip('"`').lower()
        for t in re.findall(r'\b(?:from|join)\s+([\w."`]+)', s, re.I)
    }
    if not usadas <= TABLAS_PERMITIDAS:
        return f"Error: solo puedes usar las tablas {sorted(TABLAS_PERMITIDAS)}."
    return None


@tool
def listar_tablas() -> str:
    """Lista las tablas que se pueden consultar."""
    return ", ".join(sorted(TABLAS_PERMITIDAS))


@tool
def ver_esquema(tablas: str) -> str:
    """Recibe nombres de tablas separados por comas y devuelve sus columnas
    y relaciones. Llama antes a listar_tablas. Ejemplo: products, categories"""
    insp = inspect(engine)
    salida = []
    for t in (x.strip() for x in tablas.split(",")):
        if t not in TABLAS_PERMITIDAS:
            salida.append(f"Error: la tabla '{t}' no está permitida.")
            continue
        cols = ", ".join(f"{c['name']} {c['type']}" for c in insp.get_columns(t))
        fks = "; ".join(
            f"{fk['constrained_columns']} -> {fk['referred_table']}{fk['referred_columns']}"
            for fk in insp.get_foreign_keys(t)
        )
        salida.append(f"{t}({cols})" + (f"\n  relaciones: {fks}" if fks else ""))
    return "\n".join(salida)


@tool
def revisar_sql(sql: str) -> str:
    """Revisa una consulta antes de ejecutarla. Úsala siempre antes de consultar_sql."""
    prompt = f"""{sql}
Revisa la consulta SQL de arriba buscando errores comunes: NOT IN con NULL,
UNION en lugar de UNION ALL, joins con columnas incorrectas, tipos de datos
incompatibles, identificadores mal escritos.
Si hay errores, reescríbela; si no, repítela igual.
Responde solo con la consulta SQL final, sin explicaciones."""
    out = llm.invoke(prompt).content.strip()
    return re.sub(r"```(?:sql)?", "", out).strip()


@tool
def consultar_sql(sql: str) -> str:
    """Ejecuta un SELECT y devuelve el resultado. Si da error, corrige la
    consulta y reintenta."""
    error = validar(sql)
    if error:
        return error
    try:
        # Solo lectura (Postgres rechaza escrituras) + tope de tiempo por consulta
        with engine.connect().execution_options(postgresql_readonly=True) as con:
            con.execute(text(f"SET LOCAL statement_timeout = {TIMEOUT_MS}"))
            res = con.execute(text(sql.strip().rstrip(";")))
            cols = list(res.keys())
            filas = res.fetchmany(MAX_FILAS + 1)
    except Exception as e:
        return f"Error SQL: {e}"
    datos = [dict(zip(cols, f)) for f in filas[:MAX_FILAS]]
    aviso = f"\n(Resultado truncado a {MAX_FILAS} filas)" if len(filas) > MAX_FILAS else ""
    return str(datos) + aviso
