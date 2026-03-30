import pytest
from app.nlp.ner import EntityExtractor, Entity, extract_entities


class TestEntityExtractor:
    def setup_method(self):
        self.extractor = EntityExtractor(use_spacy=True)

    def test_extract_empty_text(self):
        entities = self.extractor.extract("")
        assert entities == []

    def test_extract_action_type(self):
        text = "activa bienvenida"
        entities = self.extractor.extract(text)
        action_entities = [e for e in entities if e.label == "ACTION_TYPE"]
        assert len(action_entities) > 0

    def test_extract_modifier(self):
        text = "cambiar bienvenida"
        entities = self.extractor.extract(text)
        modifier_entities = [e for e in entities if e.label == "MODIFIER"]
        assert len(modifier_entities) > 0

    def test_extract_numbers(self):
        numbers = self.extractor.extract_numbers("pon limite de 10 mensajes en 5 segundos")
        assert 10 in numbers
        assert 5 in numbers

    def test_extract_action_type_welcome(self):
        action_type = self.extractor.extract_action_type("bienvenida con texto")
        assert action_type == "welcome"

    def test_extract_action_type_antiflood(self):
        action_type = self.extractor.extract_action_type("antiflood con 5 mensajes")
        assert action_type == "antiflood"

    def test_extract_filter_word(self):
        word = self.extractor.extract_filter_word("bloquear palabra spam")
        assert word is not None

    def test_extract_filter_word_complex(self):
        word = self.extractor.extract_filter_word("bloquea palabra malos nombres")
        assert word is not None

    def test_extract_limits(self):
        limits = self.extractor.extract_limits("pon limite de 10 mensajes en 5 segundos")
        assert limits is not None
        assert limits["limit"] == 10
        assert limits["interval"] == 5

    def test_extract_limits_with_minutes(self):
        limits = self.extractor.extract_limits("pon limite de 5 mensajes en 2 minutos")
        assert limits is not None
        assert limits["limit"] == 5
        assert limits["interval"] == 120

    def test_extract_welcome_text(self):
        text = self.extractor.extract_welcome_text("bienvenida: Hola bienvenido")
        assert text == "Hola bienvenido"

    def test_extract_welcome_text_with(self):
        text = self.extractor.extract_welcome_text("bienvenida con Bienvenido al grupo")
        assert text == "Bienvenido al grupo"

    def test_extract_welcome_text_activate(self):
        text = self.extractor.extract_welcome_text("activa bienvenida con Hola amigos")
        assert text == "Hola amigos"


class TestEntityDataclass:
    def test_entity_dataclass(self):
        entity = Entity(value="test", label="ACTION_TYPE", start=0, end=4)
        assert entity.value == "test"
        assert entity.label == "ACTION_TYPE"
        assert entity.start == 0
        assert entity.end == 4


class TestExtractEntitiesFunction:
    def test_extract_entities_function(self):
        entities = extract_entities("activa bienvenida")
        assert isinstance(entities, list)


class TestEntityExtractorSpanish:
    def setup_method(self):
        self.extractor = EntityExtractor(use_spacy=True)

    def test_spanish_entities(self):
        entities = self.extractor.extract("desactiva antiflood")
        assert len(entities) > 0

    def test_spanish_filter_word(self):
        word = self.extractor.extract_filter_word("bloquear palabra virus")
        assert word is not None

    def test_spanish_numbers(self):
        numbers = self.extractor.extract_numbers("3 mensajes en 10 segundos")
        assert 3 in numbers
        assert 10 in numbers


class TestEntityDeduplication:
    def test_no_duplicate_entities(self):
        extractor = EntityExtractor(use_spacy=False)
        entities = extractor.extract("bienvenida bienvenida")
        values = [e.value.lower() for e in entities]
        assert len(values) == len(set(values))
