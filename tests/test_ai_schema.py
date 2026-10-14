import pytest
from pydantic import ValidationError

from app.schema.ai import AskIn, AskOut


def test_thread_id_es_obligatorio():
    with pytest.raises(ValidationError):
        AskIn(pregunta="¿Cuántos productos hay?")


@pytest.mark.parametrize("thread_id", ["", "   ", "x" * 101])
def test_thread_id_invalido(thread_id):
    with pytest.raises(ValidationError):
        AskIn(pregunta="¿Cuántos productos hay?", thread_id=thread_id)


def test_contexto_opcional_hasta_300():
    assert AskIn(pregunta="abc", thread_id="t1").contexto is None
    assert AskIn(pregunta="abc", thread_id="t1", contexto="x" * 300).contexto == "x" * 300
    with pytest.raises(ValidationError):
        AskIn(pregunta="abc", thread_id="t1", contexto="x" * 301)


def test_ask_out_sugerencias_por_defecto():
    assert AskOut(respuesta="hola").sugerencias == []
