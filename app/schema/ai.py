from pydantic import BaseModel, Field


class AskIn(BaseModel):
    pregunta: str = Field(min_length=3, max_length=500)
    # misma conversación = mismo id; obligatorio para no mezclar clientes
    thread_id: str = Field(min_length=1, max_length=100, pattern=r"\S")
    contexto: str | None = Field(None, max_length=300)


class AskOut(BaseModel):
    respuesta: str
    sugerencias: list[str] = Field(default_factory=list)


class Sugerencias(BaseModel):
    sugerencias: list[str]
