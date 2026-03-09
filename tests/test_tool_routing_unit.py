from app.tools.registry import ToolRegistry, Tool, ToolType
from app.tools.router import ToolRouter, ToolCall
from app.tools.builtins import (
    register_builtin_tools,
    CALCULATOR_TOOL,
    SEARCH_TOOL,
    calculator_handler,
    convert_handler,
)


def dummy_handler(query: str) -> str:
    return f"Result: {query}"


def test_tool_registry_register():
    registry = ToolRegistry()
    tool = Tool(
        name="test_tool",
        description="A test tool",
        tool_type=ToolType.CUSTOM,
        handler=dummy_handler,
        parameters={"query": "str"}
    )
    
    registry.register(tool)
    
    assert registry.get_tool("test_tool") is not None
    assert registry.tool_exists("test_tool")


def test_tool_registry_list_tools():
    registry = ToolRegistry()
    tool1 = Tool(name="tool1", description="First tool", tool_type=ToolType.CUSTOM, handler=dummy_handler, parameters={})
    tool2 = Tool(name="tool2", description="Second tool", tool_type=ToolType.CALCULATOR, handler=dummy_handler, parameters={})
    
    registry.register(tool1)
    registry.register(tool2)
    
    tools = registry.list_tools()
    assert len(tools) == 2


def test_tool_registry_find_tools():
    registry = ToolRegistry()
    tool1 = Tool(name="calculator", description="Calculate math expressions", tool_type=ToolType.CALCULATOR, handler=dummy_handler, parameters={})
    tool2 = Tool(name="search", description="Search the web", tool_type=ToolType.SEARCH, handler=dummy_handler, parameters={})
    
    registry.register(tool1)
    registry.register(tool2)
    
    results = registry.find_tools("calculate")
    assert len(results) == 1
    assert results[0].name == "calculator"


def test_tool_registry_unregister():
    registry = ToolRegistry()
    tool = Tool(name="temp", description="Temp tool", tool_type=ToolType.CUSTOM, handler=dummy_handler, parameters={})
    
    registry.register(tool)
    assert registry.tool_exists("temp")
    
    removed = registry.unregister("temp")
    assert removed is not None
    assert not registry.tool_exists("temp")


def test_tool_router_route_finds_tools():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    
    router = ToolRouter(registry)
    
    tool_calls = router.route("calculate 2 + 2", {"tenant_id": "default"})
    
    assert len(tool_calls) > 0
    tool_names = [tc.tool for tc in tool_calls]
    assert "calculator" in tool_names


def test_tool_router_route_search():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    
    router = ToolRouter(registry)
    
    tool_calls = router.route("search for python tutorials", {"tenant_id": "default"})
    
    tool_names = [tc.tool for tc in tool_calls]
    assert "search" in tool_names


def test_tool_router_execute_tool():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    
    router = ToolRouter(registry)
    
    result = router.execute_tool("calculator", {"expression": "2 + 2"})
    assert result == "4"


def test_tool_router_execute_tool_error():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    
    router = ToolRouter(registry)
    
    result = router.execute_tool("calculator", {"expression": "2 / 0"})
    assert "Error" in result


def test_tool_router_execute_tool_call():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    
    router = ToolRouter(registry)
    
    tool_call = ToolCall(tool="calculator", parameters={"expression": "10 * 5"})
    result = router.execute_tool_call(tool_call)
    
    assert result == "50"


def test_tool_router_with_policy_engine_denies():
    from app.policies.engine import PolicyEngine
    from app.policies.models import Policy, PolicyRule, PolicyType, Action
    
    registry = ToolRegistry()
    register_builtin_tools(registry)
    
    policy_engine = PolicyEngine()
    policy = Policy(
        policy_id="deny_calculator",
        tenant_id="tenant1",
        name="Deny Calculator",
        rules=[PolicyRule(
            policy_type=PolicyType.ACCESS_CONTROL,
            name="block_calc",
            conditions={"blocked_tools": ["calculator"]},
            action=Action.DENY,
            priority=10
        )]
    )
    policy_engine.register_policy(policy)
    
    router = ToolRouter(registry, policy_engine)
    
    tool_calls = router.route("calculate 2 + 2", {"tenant_id": "tenant1"})
    
    tool_names = [tc.tool for tc in tool_calls]
    assert "calculator" not in tool_names


def test_tool_router_direct_route():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    
    router = ToolRouter(registry)
    
    tool_call = router.route_to_tool("calculator", {"expression": "3 + 3"}, {"tenant_id": "default"})
    
    assert tool_call is not None
    assert tool_call.tool == "calculator"


def test_tool_registry_list_by_type():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    
    calc_tools = registry.list_tools_by_type(ToolType.CALCULATOR)
    
    assert len(calc_tools) >= 1
    assert all(t.tool_type == ToolType.CALCULATOR for t in calc_tools)


def test_tool_router_no_matching_tools():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    
    router = ToolRouter(registry)
    
    tool_calls = router.route("this message has no matching tools", {"tenant_id": "default"})
    
    assert len(tool_calls) == 0


def test_convert_tool():
    result = convert_handler("10", "km", "mi")
    assert "6.2" in result


def test_builtin_tools_registration():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    
    tools = registry.list_tools()
    tool_names = [t.name for t in tools]
    
    assert "calculator" in tool_names
    assert "search" in tool_names
    assert "weather" in tool_names
    assert "convert" in tool_names
    assert "date" in tool_names
    assert "llm" in tool_names
