import re
import math
from typing import Any, Dict
from app.tools.registry import Tool, ToolType


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
    return f"Search results for: {query}"


def weather_handler(location: str) -> str:
    return f"Weather for {location}: (placeholder)"


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
    return f"LLM response for: {prompt}"


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

BUILTIN_TOOLS = [
    CALCULATOR_TOOL,
    SEARCH_TOOL,
    WEATHER_TOOL,
    CONVERT_TOOL,
    DATE_TOOL,
    LLM_TOOL,
]


def register_builtin_tools(registry) -> None:
    for tool in BUILTIN_TOOLS:
        registry.register(tool)
