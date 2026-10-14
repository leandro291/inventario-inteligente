import json
import os

# Antes de importar la app: valores de prueba para que nada toque Neon ni DeepSeek
# (load_dotenv no pisa variables ya definidas).
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
os.environ["DEEPSEEK_API_KEY"] = "sk-test"

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage


class FakeCheckpointer:
    def __init__(self):
        self.deleted = []

    def delete_thread(self, thread_id):
        self.deleted.append(thread_id)


class FakeAgent:
    """Imita lo que chat.py usa del agente: invoke, stream y checkpointer."""

    def __init__(self):
        self.respuesta = "Hay **3** productos."
        self.chunks = []  # items (chunk, metadata) o una Exception para cortar
        self.error = None
        self.calls = []
        self.checkpointer = FakeCheckpointer()

    def invoke(self, input, config):
        self.calls.append((input, config))
        if self.error:
            raise self.error
        return {"messages": [AIMessage(content=self.respuesta)]}

    def stream(self, input, config, stream_mode):
        self.calls.append((input, config, stream_mode))
        for item in self.chunks:
            if isinstance(item, Exception):
                raise item
            yield item


class FakeSugerir:
    def __init__(self):
        self.result = ["¿Y el stock de Bebidas?"]
        self.calls = []

    def __call__(self, pregunta, respuesta):
        self.calls.append((pregunta, respuesta))
        return self.result


@pytest.fixture
def fake_agent(monkeypatch):
    from app.ai import chat

    agent = FakeAgent()
    monkeypatch.setattr(chat, "agent", agent)
    return agent


@pytest.fixture
def fake_sugerir(monkeypatch):
    from app.ai import chat

    sugerir = FakeSugerir()
    monkeypatch.setattr(chat, "sugerir", sugerir)
    return sugerir


@pytest.fixture
def client(fake_agent, fake_sugerir):
    # Solo el router ai: main.py corre create_all contra la base real
    from app.routers import ai

    app = FastAPI()
    app.include_router(ai.router)
    return TestClient(app)


def parse_sse(texto):
    eventos = []
    for bloque in texto.strip().split("\n\n"):
        lineas = dict(linea.split(": ", 1) for linea in bloque.split("\n"))
        eventos.append((lineas["event"], json.loads(lineas["data"])))
    return eventos
