from pydantic import BaseModel, Field


class AskIn(BaseModel):
    pregunta: str = Field(min_length=3, max_length=500)
    thread_id: str = Field("default", max_length=100)  # misma conversación = mismo id


class AskOut(BaseModel):
    respuesta: str
