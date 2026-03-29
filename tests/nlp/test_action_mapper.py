import pytest
from app.nlp.action_mapper import ActionMapper, MappingResult, map_to_action
from app.agent.actions.parser import ActionParseResult


class TestActionMapper:
    def setup_method(self):
        self.mapper = ActionMapper()

    def test_map_empty_text(self):
        result = self.mapper.map("")
        assert result.action_id is None
        assert result.confidence == 0.0
        assert result.reason == "empty_message"

    def test_map_welcome_set_text(self):
        result = self.mapper.map("bienvenida: Hola bienvenido")
        assert result.action_id == "welcome.set_text"
        assert result.payload.get("text") == "Hola bienvenido"
        assert result.confidence > 0.8

    def test_map_welcome_toggle_on(self):
        result = self.mapper.map("activa bienvenida")
        assert result.action_id == "welcome.toggle"
        assert result.payload.get("enabled") == True

    def test_map_welcome_toggle_off(self):
        result = self.mapper.map("desactiva bienvenida")
        assert result.action_id == "welcome.toggle"
        assert result.payload.get("enabled") == False

    def test_map_antiflood_limits(self):
        result = self.mapper.map("pon limite de 10 mensajes en 5 segundos")
        assert result.action_id == "antiflood.set_limits"
        assert result.payload.get("limit") == 10
        assert result.payload.get("interval") == 5

    def test_map_antiflood_toggle_on(self):
        result = self.mapper.map("activa antiflood")
        assert result.action_id == "antiflood.toggle"
        assert result.payload.get("enabled") == True

    def test_map_antiflood_toggle_off(self):
        result = self.mapper.map("desactiva antiflood")
        assert result.action_id == "antiflood.toggle"
        assert result.payload.get("enabled") == False

    def test_map_antiflood_action(self):
        result = self.mapper.map("antiflood con mute")
        assert result.action_id == "antiflood.set_action"
        assert result.payload.get("action") == "mute"

    def test_map_antispam_toggle_on(self):
        result = self.mapper.map("activa antispam")
        assert result.action_id == "antispam.toggle"
        assert result.payload.get("enabled") == True

    def test_map_antispam_toggle_off(self):
        result = self.mapper.map("desactiva antispam")
        assert result.action_id == "antispam.toggle"
        assert result.payload.get("enabled") == False

    def test_map_add_filter(self):
        result = self.mapper.map("bloquear palabra spam")
        assert result.action_id == "filter.add_word"
        assert "spam" in result.payload.get("word", "")

    def test_map_remove_filter(self):
        result = self.mapper.map("desbloquea spam")
        assert result.action_id == "filter.remove_word"
        assert "spam" in result.payload.get("word", "")

    def test_map_goodbye_set_text(self):
        result = self.mapper.map("despedida: Hasta luego")
        assert result.action_id == "goodbye.set_text"
        assert result.payload.get("text") == "Hasta luego"

    def test_map_goodbye_toggle_on(self):
        result = self.mapper.map("activa despedida")
        assert result.action_id == "goodbye.toggle"
        assert result.payload.get("enabled") == True

    def test_map_goodbye_toggle_off(self):
        result = self.mapper.map("desactiva despedida")
        assert result.action_id == "goodbye.toggle"
        assert result.payload.get("enabled") == False


class TestMapToActionFunction:
    def test_map_to_action_function(self):
        result = map_to_action("activa bienvenida")
        assert isinstance(result, ActionParseResult)
        assert result.action_id is not None


class TestActionMapperSpanish:
    def setup_method(self):
        self.mapper = ActionMapper()

    def test_spanish_welcome_commands(self):
        test_cases = [
            ("bienvenida: Hola", "welcome.set_text"),
            ("Bienvenida con texto de ejemplo", "welcome.set_text"),
            ("activa bienvenida", "welcome.toggle"),
            ("desactiva bienvenida", "welcome.toggle"),
        ]
        for text, expected_action in test_cases:
            result = self.mapper.map(text)
            assert result.action_id == expected_action, f"Failed for: {text}"

    def test_spanish_antiflood_commands(self):
        test_cases = [
            ("pon limite de 5 mensajes en 3 segundos", "antiflood.set_limits"),
            ("antiflood con 10 mensajes en 20 segundos", "antiflood.set_limits"),
            ("desactiva antiflood", "antiflood.toggle"),
        ]
        for text, expected_action in test_cases:
            result = self.mapper.map(text)
            assert result.action_id == expected_action, f"Failed for: {text}"

    def test_spanish_filter_commands(self):
        test_cases = [
            ("bloquear palabra malos", "filter.add_word"),
            ("bloquea palabra spam", "filter.add_word"),
            ("desbloquea spam", "filter.remove_word"),
            ("eliminar palabra virus", "filter.remove_word"),
        ]
        for text, expected_action in test_cases:
            result = self.mapper.map(text)
            assert result.action_id == expected_action, f"Failed for: {text}"


class TestMappingResult:
    def test_mapping_result_success(self):
        result = MappingResult(success=True, action_id="test.action", confidence=0.9)
        assert result.success == True
        assert result.action_id == "test.action"

    def test_mapping_result_failure(self):
        result = MappingResult(success=False, reason="no_match")
        assert result.success == False
        assert result.reason == "no_match"


class TestActionMapperEdgeCases:
    def setup_method(self):
        self.mapper = ActionMapper()

    def test_no_intent_detected(self):
        result = self.mapper.map("hola mundo como estas")
        assert result.action_id is None
        assert result.confidence == 0.0

    def test_partial_match(self):
        result = self.mapper.map("quiero cambiar la bienvenida")
        assert result.action_id is not None or result.confidence == 0.0

    def test_antiflood_with_minutes(self):
        result = self.mapper.map("pon limite de 5 mensajes en 2 minutos")
        assert result.action_id == "antiflood.set_limits"
        assert result.payload.get("limit") == 5
        assert result.payload.get("interval") == 120
