import pytest

from app.ai import suggestions
from app.ai.suggestions import Sugerencias, sugerir


class FakeModelo:
    def __init__(self, resultado=None, error=None):
        self.resultado = resultado
        self.error = error
        self.prompts = []

    def invoke(self, prompt):
        self.prompts.append(prompt)
        if self.error:
            raise self.error
        return self.resultado


@pytest.fixture
def modelo(monkeypatch):
    fake = FakeModelo()
    monkeypatch.setattr(suggestions, "modelo_sugerencias", fake)
    return fake


def test_recorta_a_tres_y_limpia(modelo):
    modelo.resultado = Sugerencias(
        sugerencias=["  ¿Y Bebidas? ", "", "¿Y Bebidas?", "¿Stock bajo?", "¿Valor total?", "¿Otra?"]
    )
    assert sugerir("¿Cuántos productos hay?", "Hay 3.") == [
        "¿Y Bebidas?",
        "¿Stock bajo?",
        "¿Valor total?",
    ]


def test_descarta_la_pregunta_original(modelo):
    modelo.resultado = Sugerencias(sugerencias=["¿Cuántos productos hay?", "¿Y Snacks?"])
    assert sugerir("¿cuántos productos hay?", "Hay 3.") == ["¿Y Snacks?"]


def test_el_prompt_incluye_pregunta_y_respuesta(modelo):
    modelo.resultado = Sugerencias(sugerencias=[])
    sugerir("¿Cuántos productos hay?", "Hay **3**.")
    assert "¿Cuántos productos hay?" in modelo.prompts[0]
    assert "Hay **3**." in modelo.prompts[0]


def test_error_devuelve_lista_vacia(modelo):
    modelo.error = RuntimeError("timeout")
    assert sugerir("¿Cuántos productos hay?", "Hay 3.") == []


def test_resultado_none_devuelve_lista_vacia(modelo):
    modelo.resultado = None
    assert sugerir("¿Cuántos productos hay?", "Hay 3.") == []
