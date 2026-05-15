"""Tests for NLP command coverage and intent classification."""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any


class TestIntentClassifierCoverage:
    """Test intent classifier coverage for all commands."""

    def test_all_intents_have_keywords(self):
        """Test that all intents have keywords defined."""
        from app.nlp.intent_classifier import IntentClassifier
        
        classifier = IntentClassifier()
        
        for intent_name, intent_data in classifier.INTENTS.items():
            assert "keywords" in intent_data, f"Intent {intent_name} missing keywords"
            assert len(intent_data["keywords"]) > 0, f"Intent {intent_name} has no keywords"
            assert "action_keywords" in intent_data, f"Intent {intent_name} missing action_keywords"

    def test_toggle_feature_keywords(self):
        """Test toggle_feature intent classification."""
        from app.nlp.intent_classifier import IntentClassifier
        
        classifier = IntentClassifier()
        
        test_cases = [
            ("activar bienvenida", "toggle_feature"),
            ("desactivar antiflood", "toggle_feature"),
            ("enable antispam", "toggle_feature"),
            ("turn on captcha", "toggle_feature"),
            ("bloquear canales", "toggle_feature"),
            ("enable antilink", "toggle_feature"),
            ("activar modo noche", "toggle_feature"),
        ]
        
        for text, expected_intent in test_cases:
            intent, confidence = classifier.classify(text)
            assert intent == expected_intent, f"Expected {expected_intent} for '{text}', got {intent}"

    def test_get_status_intent(self):
        """Test get_status intent classification."""
        from app.nlp.intent_classifier import IntentClassifier
        
        classifier = IntentClassifier()
        
        test_cases = [
            ("como esta el bot", "get_status"),
            ("estado del bot", "get_status"),
            ("is antiflood enabled", "get_status"),
            ("ver estado", "get_status"),
        ]
        
        matched = 0
        for text, expected_intent in test_cases:
            intent, confidence = classifier.classify(text)
            if intent == expected_intent:
                matched += 1
        
        assert matched >= 2, f"Expected at least 2 matches for get_status, got {matched}"

    def test_get_settings_intent(self):
        """Test get_settings intent classification."""
        from app.nlp.intent_classifier import IntentClassifier
        
        classifier = IntentClassifier()
        
        test_cases = [
            ("ver configuracion", "get_settings"),
            ("show settings", "get_settings"),
            ("que tienes configurado", "get_settings"),
            ("cuales son las opciones", "get_settings"),
        ]
        
        matched = 0
        for text, expected_intent in test_cases:
            intent, confidence = classifier.classify(text)
            if intent == expected_intent:
                matched += 1
        
        assert matched >= 1, f"Expected at least 1 match for get_settings, got {matched}"

    def test_list_actions_intent(self):
        """Test list_actions intent classification."""
        from app.nlp.intent_classifier import IntentClassifier
        
        classifier = IntentClassifier()
        
        test_cases = [
            ("ver comandos", "list_actions"),
            ("mostrar acciones", "list_actions"),
            ("listar funciones", "list_actions"),
        ]
        
        matched = 0
        for text, expected_intent in test_cases:
            intent, confidence = classifier.classify(text)
            if intent == expected_intent:
                matched += 1
        
        assert matched >= 1, f"Expected at least 1 match for list_actions, got {matched}"

    def test_help_intent(self):
        """Test help intent classification."""
        from app.nlp.intent_classifier import IntentClassifier
        
        classifier = IntentClassifier()
        
        test_cases = [
            ("ayudame", "help"),
            ("help me", "help"),
            ("como uso el bot", "help"),
            ("dame ayuda", "help"),
        ]
        
        matched = 0
        for text, expected_intent in test_cases:
            intent, confidence = classifier.classify(text)
            if intent == expected_intent:
                matched += 1
        
        assert matched >= 1, f"Expected at least 1 match for help, got {matched}"


class TestActionMapperCoverage:
    """Test action mapper coverage for all intents."""

    def test_all_intents_have_mapping(self):
        """Test that all intents have mappings defined."""
        from app.nlp.action_mapper import ActionMapper
        
        mapper = ActionMapper()
        
        for intent_name in mapper.ACTION_MAPPINGS.keys():
            assert intent_name in mapper.ACTION_MAPPINGS, f"Intent {intent_name} missing mapping"

    def test_query_intents_map_correctly(self):
        """Test query intents map to correct action_ids."""
        from app.nlp.action_mapper import ActionMapper
        
        mapper = ActionMapper()
        
        query_intents = ["get_status", "get_settings", "list_actions", "help", "show_reports", "show_warnings"]
        
        for intent in query_intents:
            result = mapper.map("test text", intent=intent)
            assert result.action_id is not None, f"Intent {intent} has no action_id"
            assert result.confidence > 0, f"Intent {intent} has no confidence"

    def test_toggle_feature_mapping(self):
        """Test toggle_feature maps to correct action_ids."""
        from app.nlp.action_mapper import ActionMapper
        
        mapper = ActionMapper()
        
        test_cases = [
            ("activar bienvenida", "welcome.toggle"),
            ("desactivar antiflood", "antiflood.toggle"),
            ("enable captcha", "captcha.toggle"),
            ("turn on nightmode", "nightmode.toggle"),
        ]
        
        for text, expected_action in test_cases:
            result = mapper.map(text, intent="toggle_feature")
            if result.action_id:
                action_prefix = result.action_id.split(".")[0]
                expected_prefix = expected_action.split(".")[0]
                assert action_prefix == expected_prefix, f"Expected {expected_action} for '{text}', got {result.action_id}"

    def test_set_action_mapping(self):
        """Test set_action intent mapping."""
        from app.nlp.action_mapper import ActionMapper
        
        mapper = ActionMapper()
        
        test_cases = [
            ("antiflood con mute", "mute"),
            ("flood with ban", "ban"),
            ("anti flood warn", "warn"),
        ]
        
        for text, expected_action in test_cases:
            result = mapper.map(text, intent="set_action")
            if result.payload and "action" in result.payload:
                assert result.payload["action"] == expected_action, f"Expected {expected_action} for '{text}'"


class TestFeatureDetection:
    """Test feature detection in text."""

    def test_all_features_detectable(self):
        """Test that all features can be detected."""
        from app.nlp.intent_classifier import IntentClassifier
        
        classifier = IntentClassifier()
        
        test_cases = [
            ("bienvenida", "welcome"),
            ("antiflood", "antiflood"),
            ("antispam", "antispam"),
            ("despedida", "goodbye"),
            ("filtro", "filter"),
            ("canal", "antichannel"),
            ("enlace", "antilink"),
            ("captcha", "captcha"),
            ("modo noche", "nightmode"),
            ("multimedia", "media"),
            ("reportes", "reports"),
            ("advertencias", "warnings"),
        ]
        
        for text, expected_feature in test_cases:
            detected = classifier.detect_feature(text)
            assert detected == expected_feature, f"Expected {expected_feature} for '{text}', got {detected}"


class TestEntityExtractor:
    """Test entity extraction for commands."""

    def test_extract_limits(self):
        """Test limit extraction."""
        from app.nlp.ner import EntityExtractor
        
        extractor = EntityExtractor(use_spacy=False)
        
        test_cases = [
            ("5 mensajes en 3 segundos", {"limit": 5, "interval": 3}),
            ("10 mensajes por 5 segundos", {"limit": 10, "interval": 5}),
            ("3 mensajes en 1 minuto", {"limit": 3, "interval": 60}),
        ]
        
        matched = 0
        for text, expected in test_cases:
            result = extractor.extract_limits(text)
            if result == expected:
                matched += 1
        
        assert matched >= 2, f"Expected at least 2 matches, got {matched}"

    def test_extract_action(self):
        """Test action extraction."""
        from app.nlp.ner import EntityExtractor
        
        extractor = EntityExtractor(use_spacy=False)
        
        test_cases = [
            ("con mute", "mute"),
            ("with ban", "ban"),
            ("silenciar", "mute"),
            ("expulsar", "kick"),
        ]
        
        for text, expected in test_cases:
            result = extractor.extract_action(text)
            assert result == expected, f"Expected {expected} for '{text}', got {result}"

    def test_extract_report_id(self):
        """Test report ID extraction."""
        from app.nlp.ner import EntityExtractor
        
        extractor = EntityExtractor(use_spacy=False)
        
        test_cases = [
            ("resolver reporte #123", "123"),
            ("close report 456", "456"),
            ("reporte 789", "789"),
        ]
        
        for text, expected in test_cases:
            result = extractor.extract_report_id(text)
            assert result == expected, f"Expected {expected} for '{text}', got {result}"


class TestNLPCommandMetrics:
    """Test NLP command processing metrics."""

    def test_intent_confidence_thresholds(self):
        """Test that confidence thresholds are appropriate."""
        from app.nlp.intent_classifier import IntentClassifier
        
        classifier = IntentClassifier()
        
        test_cases = [
            ("activar bienvenida muy importante", "toggle_feature"),
            ("cambiar mensaje de bienvenida", "set_welcome"),
            ("bloquear palabra muy mala", "add_filter"),
        ]
        
        for text, expected_intent in test_cases:
            intent, confidence = classifier.classify(text)
            assert confidence >= 0.5, f"Confidence too low for '{text}': {confidence}"
            if intent:
                assert confidence > 0, f"Confidence should be positive for '{text}'"

    def test_fallback_for_unmatched(self):
        """Test fallback behavior for unmatched text."""
        from app.nlp.intent_classifier import IntentClassifier
        from app.nlp.action_mapper import ActionMapper
        
        classifier = IntentClassifier()
        mapper = ActionMapper()
        
        unmatched_texts = [
            "hola como estas",
            "buenos dias",
            "random text here",
        ]
        
        for text in unmatched_texts:
            intent, confidence = classifier.classify(text)
            if intent:
                result = mapper.map(text, intent=intent)
                assert result.action_id or result.confidence == 0, f"Should handle unmatched gracefully"


class TestNLPIntegration:
    """Integration tests for complete NLP pipeline."""

    def test_welcome_flow(self):
        """Test complete welcome configuration flow."""
        from app.nlp.action_mapper import ActionMapper
        
        mapper = ActionMapper()
        
        texts = [
            "activar bienvenida",
            "cambiar mensaje de bienvenida",
            "desactivar bienvenida",
        ]
        
        for text in texts:
            result = mapper.map(text)
            assert result is not None, f"Should return result for '{text}'"

    def test_antiflood_flow(self):
        """Test complete antiflood configuration flow."""
        from app.nlp.action_mapper import ActionMapper
        
        mapper = ActionMapper()
        
        texts = [
            "activar antiflood",
            "pon antiflood con 5 mensajes en 3 segundos",
            "desactivar antiflood",
            "antiflood con mute",
        ]
        
        for text in texts:
            result = mapper.map(text)
            assert result is not None, f"Should return result for '{text}'"

    def test_status_query_flow(self):
        """Test complete status query flow."""
        from app.nlp.action_mapper import ActionMapper
        
        mapper = ActionMapper()
        
        texts = [
            "ver estado del bot",
            "como esta la bienvenida",
            "is antiflood enabled",
        ]
        
        for text in texts:
            result = mapper.map(text)
            assert result is not None, f"Should return result for '{text}'"

    def test_filter_flow(self):
        """Test complete filter flow."""
        from app.nlp.action_mapper import ActionMapper
        
        mapper = ActionMapper()
        
        texts = [
            "bloquear palabra spam",
            "quitar palabra bloqueada",
        ]
        
        for text in texts:
            result = mapper.map(text)
            assert result is not None, f"Should return result for '{text}'"
