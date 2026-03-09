from app.guardrails.guardrail import Guardrails, GuardrailResult


_default_guardrails = Guardrails(name="default")

_default_guardrails.add_blocked_pattern(
    r'\b\d{3}-\d{2}-\d{4}\b',
    "SSN"
)

_default_guardrails.add_blocked_pattern(
    r'\b\d{16}\b',
    "Credit Card"
)

_default_guardrails.add_blocked_pattern(
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    "Email"
)

_default_guardrails.add_blocked_pattern(
    r'\b\+?1?\s*\-?\.?\s*\(?\d{3}\)?[\s\-\.]*\d{3}[\s\-\.]*\d{4}\b',
    "Phone Number"
)

_default_guardrails.add_blocked_pattern(
    r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
    "IP Address"
)

_default_guardrails.add_blocked_pattern(
    r'\b[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2}\b',
    "UK Postal Code"
)

_default_guardrails.add_blocked_pattern(
    r'\b\d{5}(?:-\d{4})?\b',
    "US ZIP Code"
)

_default_guardrails.add_blocked_keyword("password")
_default_guardrails.add_blocked_keyword("secret")
_default_guardrails.add_blocked_keyword("token")
_default_guardrails.add_blocked_keyword("api_key")
_default_guardrails.add_blocked_keyword("apikey")


def get_default_guardrails() -> Guardrails:
    return _default_guardrails


def apply_guardrails(content: str) -> GuardrailResult:
    return _default_guardrails.check(content)


def filter_sensitive_data(content: str) -> str:
    return _default_guardrails.filter(content)


def create_custom_guardrails(name: str = "custom") -> Guardrails:
    guardrails = Guardrails(name=name)
    
    guardrails.add_blocked_pattern(r'\b\d{3}-\d{2}-\d{4}\b', "SSN")
    guardrails.add_blocked_pattern(r'\b\d{16}\b', "Credit Card")
    guardrails.add_blocked_pattern(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', "Email")
    
    return guardrails
