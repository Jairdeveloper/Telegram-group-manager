import pytest
from app.guardrails.guardrail import Guardrails, GuardrailResult
from app.guardrails.middleware import (
    apply_guardrails,
    filter_sensitive_data,
    get_default_guardrails,
    create_custom_guardrails
)


def test_guardrail_blocks_ssn():
    guardrails = Guardrails()
    guardrails.add_blocked_pattern(r'\b\d{3}-\d{2}-\d{4}\b', "SSN")
    
    result = guardrails.check("My SSN is 123-45-6789")
    assert result.allowed is False
    assert "SSN" in result.reason


def test_guardrail_blocks_credit_card():
    guardrails = Guardrails()
    guardrails.add_blocked_pattern(r'\b\d{16}\b', "Credit Card")
    
    result = guardrails.check("Card number: 1234567890123456")
    assert result.allowed is False
    assert "Credit Card" in result.reason


def test_guardrail_blocks_email():
    guardrails = Guardrails()
    guardrails.add_blocked_pattern(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', "Email")
    
    result = guardrails.check("Email me at test@example.com")
    assert result.allowed is False
    assert "Email" in result.reason


def test_guardrail_allows_clean_content():
    guardrails = Guardrails()
    guardrails.add_blocked_pattern(r'\b\d{3}-\d{2}-\d{4}\b', "SSN")
    
    result = guardrails.check("Hello, how are you?")
    assert result.allowed is True
    assert result.filtered_content == "Hello, how are you?"


def test_guardrail_blocks_keyword():
    guardrails = Guardrails()
    guardrails.add_blocked_keyword("password")
    
    result = guardrails.check("My password is secret123")
    assert result.allowed is False


def test_guardrail_filter_masks_content():
    guardrails = Guardrails()
    guardrails.add_blocked_pattern(r'\b\d{3}-\d{2}-\d{4}\b', "SSN")
    
    filtered = guardrails.filter("SSN: 123-45-6789")
    assert "123-45-6789" not in filtered


def test_guardrail_multiple_patterns():
    guardrails = Guardrails()
    guardrails.add_blocked_pattern(r'\b\d{3}-\d{2}-\d{4}\b', "SSN")
    guardrails.add_blocked_pattern(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', "Email")
    
    result = guardrails.check("SSN: 123-45-6789, Email: test@example.com")
    assert result.allowed is False


def test_guardrail_allowed_patterns():
    guardrails = Guardrails()
    guardrails.add_allowed_pattern(r'^hello.*world$')
    
    result = guardrails.check("hello beautiful world")
    assert result.allowed is True
    
    result2 = guardrails.check("something else")
    assert result2.allowed is False


def test_guardrail_get_stats():
    guardrails = Guardrails()
    guardrails.add_blocked_pattern(r'\b\d{3}-\d{2}-\d{4}\b', "SSN")
    guardrails.add_blocked_keyword("password")
    
    stats = guardrails.get_stats()
    assert stats["blocked_patterns_count"] == 1
    assert stats["blocked_keywords_count"] == 1


def test_guardrail_list_patterns():
    guardrails = Guardrails()
    guardrails.add_blocked_pattern(r'\b\d{3}-\d{2}-\d{4}\b', "SSN")
    guardrails.add_blocked_pattern(r'\b\d{16}\b', "Credit Card")
    
    patterns = guardrails.list_blocked_patterns()
    assert "SSN" in patterns
    assert "Credit Card" in patterns


def test_guardrail_remove_pattern():
    guardrails = Guardrails()
    guardrails.add_blocked_pattern(r'\b\d{3}-\d{2}-\d{4}\b', "SSN")
    
    assert guardrails.remove_blocked_pattern("SSN") is True
    assert guardrails.list_blocked_patterns() == []


def test_guardrail_clear_patterns():
    guardrails = Guardrails()
    guardrails.add_blocked_pattern(r'\b\d{3}-\d{2}-\d{4}\b', "SSN")
    guardrails.add_blocked_keyword("password")
    
    guardrails.clear_patterns()
    
    assert guardrails.list_blocked_patterns() == []
    assert guardrails.list_blocked_keywords() == []


def test_middleware_default_guardrails_blocks_ssn():
    result = apply_guardrails("My SSN is 123-45-6789")
    assert result.allowed is False


def test_middleware_default_guardrails_blocks_email():
    result = apply_guardrails("Email: test@example.com")
    assert result.allowed is False


def test_middleware_default_guardrails_blocks_phone():
    result = apply_guardrails("Call me at 555-123-4567")
    assert result.allowed is False


def test_middleware_filter_sensitive_data():
    filtered = filter_sensitive_data("SSN: 123-45-6789")
    assert "123-45-6789" not in filtered


def test_middleware_get_default_guardrails():
    guardrails = get_default_guardrails()
    assert guardrails.name == "default"
    assert len(guardrails.list_blocked_patterns()) > 0


def test_middleware_create_custom_guardrails():
    guardrails = create_custom_guardrails("my_custom")
    assert guardrails.name == "my_custom"
    assert len(guardrails.list_blocked_patterns()) > 0


def test_guardrail_matches_contain_details():
    guardrails = Guardrails()
    guardrails.add_blocked_pattern(r'\b\d{3}-\d{2}-\d{4}\b', "SSN")
    
    result = guardrails.check("SSN: 123-45-6789")
    assert len(result.matches) > 0
    assert result.matches[0]["type"] == "pattern"
    assert result.matches[0]["description"] == "SSN"


def test_guardrail_filter_specific():
    guardrails = Guardrails()
    guardrails.add_blocked_pattern(r'\b\d{3}-\d{2}-\d{4}\b', "SSN")
    guardrails.add_blocked_pattern(r'\b\d{16}\b', "Credit Card")
    
    filtered = guardrails.filter_specific("SSN: 123-45-6789", "SSN")
    assert "123-45-6789" not in filtered
    
    filtered2 = guardrails.filter_specific("SSN: 123-45-6789", "Credit Card")
    assert "123-45-6789" in filtered2


def test_guardrail_case_insensitive():
    guardrails = Guardrails()
    guardrails.add_blocked_keyword("password")
    
    result = guardrails.check("My PASSWORD is secret")
    assert result.allowed is False


def test_guardrail_allows_ip_address():
    guardrails = Guardrails()
    guardrails.add_blocked_pattern(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', "IP Address")
    
    result = guardrails.check("Server at 192.168.1.1")
    assert result.allowed is False


def test_guardrail_blocks_api_key():
    result = apply_guardrails("My api_key is abc123secret")
    assert result.allowed is False
