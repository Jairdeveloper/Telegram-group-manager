import re
import math
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse

import httpx

from app.config.settings import load_api_settings
from app.guardrails.middleware import apply_guardrails, filter_sensitive_data
from app.tools.registry import Tool, ToolType
from chat_service.llm.factory import LLMFactory, config_from_settings
from chat_service.llm.base import LLMError


def calculator_handler(expression: str) -> str:
    try:
        allowed = set("0123456789+-*/.() ")
        if any(c not in allowed for c in expression):
            return "Error: Invalid characters in expression"
        result = eval(expression)
        return str(result)
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error: {str(e)}"


def search_handler(query: str) -> str:
    guard = _guard_inputs([query])
    if guard:
        return guard

    settings = load_api_settings()
    if not settings.search_api_url:
        return "Error: SEARCH_API_URL not configured"
    provider = (settings.search_provider or "duckduckgo").lower()
    if provider != "duckduckgo":
        return f"Error: Unsupported search provider '{provider}'"

    params = {
        "q": query,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1,
    }
    if settings.search_api_key:
        params["api_key"] = settings.search_api_key

    try:
        response = httpx.get(
            settings.search_api_url,
            params=params,
            timeout=settings.search_timeout,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        return f"Error: Search failed - {exc}"

    abstract = data.get("AbstractText")
    if abstract:
        return _sanitize_output(abstract)

    related = data.get("RelatedTopics", [])
    snippets: List[str] = []
    for item in related:
        if isinstance(item, dict) and item.get("Text"):
            snippets.append(item["Text"])
        if len(snippets) >= 3:
            break

    if snippets:
        return _sanitize_output(" | ".join(snippets))

    return "No results found"


def weather_handler(location: str) -> str:
    guard = _guard_inputs([location])
    if guard:
        return guard

    settings = load_api_settings()
    if not settings.weather_api_key:
        return "Error: WEATHER_API_KEY not configured"

    params = {
        "q": location,
        "appid": settings.weather_api_key,
        "units": settings.weather_units,
        "lang": settings.weather_lang,
    }
    try:
        response = httpx.get(
            settings.weather_api_url,
            params=params,
            timeout=settings.weather_timeout,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        return f"Error: Weather lookup failed - {exc}"

    main = data.get("main", {})
    weather = data.get("weather", [{}])[0]
    temp = main.get("temp")
    desc = weather.get("description")
    if temp is None and not desc:
        return "Error: Weather response incomplete"

    parts = [f"Weather for {location}:"]
    if desc:
        parts.append(str(desc))
    if temp is not None:
        parts.append(f"{temp}°")
    return _sanitize_output(" ".join(parts))


def convert_handler(value: str, from_unit: str, to_unit: str) -> str:
    conversions = {
        ("km", "mi"): 0.621371,
        ("mi", "km"): 1.60934,
        ("kg", "lb"): 2.20462,
        ("lb", "kg"): 0.453592,
        ("c", "f"): lambda x: x * 9/5 + 32,
        ("f", "c"): lambda x: (x - 32) * 5/9,
        ("m", "ft"): 3.28084,
        ("ft", "m"): 0.3048,
    }
    
    key = (from_unit.lower(), to_unit.lower())
    if key not in conversions:
        return f"Error: Conversion from {from_unit} to {to_unit} not supported"
    
    try:
        value = float(value)
    except ValueError:
        return f"Error: Invalid numeric value: {value}"
    
    conv = conversions[key]
    if callable(conv):
        result = conv(value)
    else:
        result = value * conv
    
    return str(result)


def date_handler(action: str, format: str = "%Y-%m-%d") -> str:
    from datetime import datetime, timedelta
    
    action = action.lower()
    if action == "now":
        return datetime.now().strftime(format)
    elif action == "today":
        return datetime.now().strftime(format)
    elif action == "tomorrow":
        return (datetime.now() + timedelta(days=1)).strftime(format)
    elif action == "yesterday":
        return (datetime.now() - timedelta(days=1)).strftime(format)
    else:
        return f"Error: Unknown action '{action}'. Use: now, today, tomorrow, yesterday"


def llm_handler(prompt: str, **kwargs) -> str:
    settings = load_api_settings()
    if not settings.llm_enabled:
        return "LLM disabled. Set LLM_ENABLED=true to enable."
    config = config_from_settings(settings)
    provider = LLMFactory.get_provider(config)
    try:
        guard = _guard_inputs([prompt])
        if guard:
            return guard
        output = provider.generate(prompt)
        return _sanitize_output(output)
    except LLMError as exc:
        return f"LLM error: {exc}"


def database_handler(query: str) -> str:
    guard = _guard_inputs([query])
    if guard:
        return guard

    settings = load_api_settings()
    if not settings.is_postgres_enabled():
        return "Error: DATABASE_URL not configured"

    clean = (query or "").strip()
    lowered = clean.lower()
    if not (lowered.startswith("select") or lowered.startswith("with")):
        return "Error: Only SELECT queries are allowed"
    if ";" in clean.rstrip(";"):
        return "Error: Multiple statements are not allowed"

    limit = settings.database_max_rows
    if "limit" not in lowered:
        clean = f"{clean} LIMIT {limit}"

    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text(clean))
            rows = result.fetchmany(limit)
            if not rows:
                return "No rows returned"
            headers = result.keys()
            lines = [", ".join(headers)]
            for row in rows:
                values = [str(value) for value in row]
                lines.append(", ".join(values))
            return _sanitize_output("\n".join(lines))
    except Exception as exc:
        return f"Error: Database query failed - {exc}"


def http_get_handler(url: str) -> str:
    guard = _guard_inputs([url])
    if guard:
        return guard

    settings = load_api_settings()
    allowed_hosts = _parse_allowed_hosts(settings.http_allowed_hosts)
    if not allowed_hosts:
        return "Error: HTTP_ALLOWED_HOSTS not configured"

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return "Error: Only http/https URLs are allowed"
    host = parsed.hostname or ""
    if host not in allowed_hosts:
        return f"Error: Host '{host}' not allowed"

    try:
        response = httpx.get(
            url,
            timeout=settings.http_timeout,
            follow_redirects=settings.http_follow_redirects,
        )
        response.raise_for_status()
        text = response.text[: settings.http_max_bytes]
        return _sanitize_output(f"HTTP {response.status_code}: {text}")
    except Exception as exc:
        return f"Error: HTTP request failed - {exc}"


CALCULATOR_TOOL = Tool(
    name="calculator",
    description="Calculate mathematical expressions",
    tool_type=ToolType.CALCULATOR,
    handler=calculator_handler,
    parameters={"expression": "str"}
)

SEARCH_TOOL = Tool(
    name="search",
    description="Search the web for information",
    tool_type=ToolType.SEARCH,
    handler=search_handler,
    parameters={"query": "str"}
)

WEATHER_TOOL = Tool(
    name="weather",
    description="Get weather information for a location",
    tool_type=ToolType.WEATHER,
    handler=weather_handler,
    parameters={"location": "str"}
)

CONVERT_TOOL = Tool(
    name="convert",
    description="Convert between different units (km to miles, kg to pounds, etc.)",
    tool_type=ToolType.CUSTOM,
    handler=convert_handler,
    parameters={"value": "str", "from_unit": "str", "to_unit": "str"}
)

DATE_TOOL = Tool(
    name="date",
    description="Get current date, today, tomorrow or yesterday",
    tool_type=ToolType.CUSTOM,
    handler=date_handler,
    parameters={"action": "str", "format": "str"}
)

LLM_TOOL = Tool(
    name="llm",
    description="Process text with LLM",
    tool_type=ToolType.LLM,
    handler=llm_handler,
    parameters={"prompt": "str"}
)

DATABASE_TOOL = Tool(
    name="database",
    description="Run read-only SQL queries (SELECT only)",
    tool_type=ToolType.DATABASE,
    handler=database_handler,
    parameters={"query": "str"}
)

HTTP_TOOL = Tool(
    name="http",
    description="Fetch an HTTP URL from allowed hosts",
    tool_type=ToolType.HTTP,
    handler=http_get_handler,
    parameters={"url": "str"}
)

BUILTIN_TOOLS = [
    CALCULATOR_TOOL,
    SEARCH_TOOL,
    WEATHER_TOOL,
    CONVERT_TOOL,
    DATE_TOOL,
    LLM_TOOL,
    DATABASE_TOOL,
    HTTP_TOOL,
]


def register_builtin_tools(registry) -> None:
    for tool in BUILTIN_TOOLS:
        registry.register(tool)


def _guard_inputs(values: Iterable[Optional[str]]) -> Optional[str]:
    for value in values:
        if value is None:
            continue
        result = apply_guardrails(value)
        if not result.allowed:
            return f"Error: Input blocked by guardrails ({result.reason})"
    return None


def _sanitize_output(text: str) -> str:
    return filter_sensitive_data(text or "")


def _parse_allowed_hosts(raw: str) -> List[str]:
    if not raw:
        return []
    return [token.strip() for token in raw.split(",") if token.strip()]
