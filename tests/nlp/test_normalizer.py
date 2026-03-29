import pytest
from app.nlp.normalizer import TextNormalizer, normalize_text, normalize_text_keep_numbers


class TestTextNormalizer:
    def setup_method(self):
        self.normalizer = TextNormalizer()

    def test_normalize_empty_string(self):
        assert self.normalizer.normalize("") == ""
        assert self.normalizer.normalize("   ") == ""

    def test_normalize_lowercase(self):
        assert self.normalizer.normalize("HOLA MUNDO") == "hola mundo"
        assert self.normalizer.normalize("HeLLo WoRLd") == "hello world"

    def test_normalize_remove_numbers(self):
        assert self.normalizer.normalize("tengo 5 mensajes") == "tengo mensajes"
        assert self.normalizer.normalize("123 texto 456") == "texto"

    def test_normalize_remove_punctuation(self):
        assert self.normalizer.normalize("hola, mundo!") == "hola mundo"
        assert self.normalizer.normalize("que...??").strip() == "que"
        assert self.normalizer.normalize("bienvenida: hola") == "bienvenida hola"

    def test_normalize_extra_whitespace(self):
        assert self.normalizer.normalize("hola    mundo") == "hola mundo"
        assert self.normalizer.normalize("  hola   mundo  ") == "hola mundo"

    def test_normalize_complete(self):
        result = self.normalizer.normalize("HOLA, tengo 3 mensajes!!!")
        assert result == "hola tengo mensajes"

    def test_normalize_preserve_case(self):
        normalizer = TextNormalizer(lowercase=False)
        assert normalizer.normalize("HOLA MUNDO") == "HOLA MUNDO"
        assert normalizer.normalize("Hola, Mundo!") == "Hola Mundo"

    def test_normalize_keep_numbers(self):
        result = self.normalizer.normalize_keep_numbers("10 mensajes en 5 segundos")
        assert result == "10 mensajes en 5 segundos"

    def test_normalize_keep_numbers_removes_punctuation(self):
        result = self.normalizer.normalize_keep_numbers("10 mensajes en 5 segundos!!!")
        assert result == "10 mensajes en 5 segundos"

    def test_normalize_spanish_commands(self):
        assert self.normalizer.normalize("Activa bienvenida") == "activa bienvenida"
        assert self.normalizer.normalize("DESACTIVA antiflood") == "desactiva antiflood"
        assert self.normalizer.normalize("Pon limite de 5 mensajes") == "pon limite de mensajes"

    def test_normalize_welcome_commands(self):
        assert self.normalizer.normalize("bienvenida: Hola") == "bienvenida hola"
        assert self.normalizer.normalize("Bienvenida con texto") == "bienvenida con texto"

    def test_normalize_filter_commands(self):
        assert self.normalizer.normalize("bloquear palabra spam") == "bloquear palabra spam"
        assert self.normalizer.normalize("bloquea spam!!!") == "bloquea spam"


class TestNormalizeFunctions:
    def test_normalize_text_function(self):
        result = normalize_text("HOLA MUNDO")
        assert result == "hola mundo"

    def test_normalize_text_keep_numbers_function(self):
        result = normalize_text_keep_numbers("10 mensajes")
        assert "10" in result
