import pytest
from app.nlp.intent_classifier import IntentClassifier, IntentMatch, classify_intent


class TestIntentClassifier:
    def setup_method(self):
        self.classifier = IntentClassifier()

    def test_classify_empty_text(self):
        intent, confidence = self.classifier.classify("")
        assert intent is None
        assert confidence == 0.0

    def test_classify_set_welcome(self):
        intent, confidence = self.classifier.classify("quiero cambiar la bienvenida")
        assert intent == "set_welcome"
        assert confidence > 0.5

    def test_classify_toggle_feature(self):
        intent, confidence = self.classifier.classify("activa antiflood")
        assert intent == "toggle_feature"
        assert confidence > 0.5

    def test_classify_set_limit(self):
        intent, confidence = self.classifier.classify("pon limite de 5 mensajes")
        assert intent == "set_limit"
        assert confidence > 0.5

    def test_classify_add_filter(self):
        intent, confidence = self.classifier.classify("bloquear palabra spam")
        assert intent == "add_filter"
        assert confidence > 0.5

    def test_classify_remove_filter(self):
        intent, confidence = self.classifier.classify("desbloquea spam")
        assert intent == "remove_filter"
        assert confidence > 0.5

    def test_classify_no_match(self):
        intent, confidence = self.classifier.classify("hola mundo como estas")
        assert intent is None

    def test_classify_with_details(self):
        matches = self.classifier.classify_with_details("activa bienvenida")
        assert len(matches) > 0
        assert all(isinstance(m, IntentMatch) for m in matches)

    def test_detect_feature_welcome(self):
        feature = self.classifier.detect_feature("bienvenida con texto")
        assert feature == "welcome"

    def test_detect_feature_antiflood(self):
        feature = self.classifier.detect_feature("antiflood con 10 mensajes")
        assert feature == "antiflood"

    def test_detect_feature_filter(self):
        feature = self.classifier.detect_feature("agregar filtro palabra")
        assert feature == "filter"

    def test_is_toggle_on(self):
        assert self.classifier.is_toggle_on("activa bienvenida")
        assert self.classifier.is_toggle_on("pon antiflood")
        assert self.classifier.is_toggle_on("enable antispam")

    def test_is_toggle_off(self):
        assert self.classifier.is_toggle_off("desactiva antiflood")
        assert self.classifier.is_toggle_off("apagar bienvenida")
        assert self.classifier.is_toggle_off("disable antispam")

    def test_extract_action_verb(self):
        verb = self.classifier.extract_action_verb("quiero cambiar la bienvenida")
        assert verb in ["cambiar", "cambia"]

    def test_confidence_increases_with_keywords(self):
        intent1, conf1 = self.classifier.classify("bienvenida")
        intent2, conf2 = self.classifier.classify("quiero cambiar la bienvenida")
        assert conf2 >= conf1


class TestClassifyIntentFunction:
    def test_classify_intent_function(self):
        intent, confidence = classify_intent("activa bienvenida")
        assert intent == "toggle_feature"
        assert confidence > 0.0


class TestIntentClassifierSpanish:
    def setup_method(self):
        self.classifier = IntentClassifier()

    def test_spanish_commands(self):
        test_cases = [
            ("cambia la bienvenida", "set_welcome"),
            ("desactiva antiflood", "toggle_feature"),
            ("pon limite de 10 mensajes", "set_limit"),
            ("bloquea la palabra spam", "add_filter"),
            ("quitar filtro spam", "remove_filter"),
        ]
        for text, expected_intent in test_cases:
            intent, confidence = self.classifier.classify(text)
            assert intent == expected_intent, f"Failed for: {text}"


class TestIntentMatch:
    def test_intent_match_dataclass(self):
        match = IntentMatch(intent="test", confidence=0.8, matched_keywords=["test"])
        assert match.intent == "test"
        assert match.confidence == 0.8
        assert match.matched_keywords == ["test"]


class TestNewIntents:
    def setup_method(self):
        self.classifier = IntentClassifier()

    def test_classify_get_status(self):
        intent, confidence = self.classifier.classify("como esta el antiflood")
        assert intent in ("get_status", "toggle_feature")
        assert confidence > 0

    def test_classify_get_settings(self):
        intent, confidence = self.classifier.classify("cuales son los filtros")
        assert intent in ("get_settings", "get_status", "remove_filter")
        assert confidence > 0

    def test_classify_help(self):
        intent, confidence = self.classifier.classify("ayudame con los comandos")
        assert intent == "help"
        assert confidence > 0

    def test_classify_list_actions(self):
        intent, confidence = self.classifier.classify("que puedes hacer")
        assert intent in ("list_actions", "help")
        assert confidence > 0

    def test_intents_available(self):
        assert "get_status" in self.classifier.INTENTS
        assert "get_settings" in self.classifier.INTENTS
        assert "help" in self.classifier.INTENTS
        assert "list_actions" in self.classifier.INTENTS
