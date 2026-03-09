from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
from app.tools.registry import ToolRegistry, Tool
from app.policies.engine import PolicyEngine
from app.policies.models import Action


@dataclass
class ToolCall:
    tool: str
    parameters: Dict[str, Any]
    warning: Optional[str] = None


class ToolRouter:
    def __init__(self, tool_registry: ToolRegistry, policy_engine: Optional[PolicyEngine] = None):
        self.registry = tool_registry
        self.policy_engine = policy_engine
    
    def set_policy_engine(self, policy_engine: PolicyEngine) -> None:
        self.policy_engine = policy_engine
    
    def route(self, user_message: str, context: Dict[str, Any]) -> List[ToolCall]:
        tools_to_call = []
        
        matching_tools = self.registry.find_tools(user_message)
        
        for tool in matching_tools:
            if self.policy_engine:
                action, msg = self.policy_engine.evaluate(
                    context.get("tenant_id", "default"),
                    {"tool_name": tool.name, "action": "tool_call"}
                )
                
                if action == Action.DENY:
                    continue
                elif action == Action.WARN:
                    tools_to_call.append(ToolCall(
                        tool=tool.name,
                        parameters=self._extract_parameters(tool, user_message),
                        warning=msg
                    ))
                else:
                    tools_to_call.append(ToolCall(
                        tool=tool.name,
                        parameters=self._extract_parameters(tool, user_message)
                    ))
            else:
                tools_to_call.append(ToolCall(
                    tool=tool.name,
                    parameters=self._extract_parameters(tool, user_message)
                ))
        
        return tools_to_call
    
    def route_to_tool(self, tool_name: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Optional[ToolCall]:
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return None
        
        if self.policy_engine:
            action, msg = self.policy_engine.evaluate(
                context.get("tenant_id", "default"),
                {"tool_name": tool.name, "action": "tool_call"}
            )
            
            if action == Action.DENY:
                return None
            
            return ToolCall(
                tool=tool.name,
                parameters=parameters,
                warning=msg if action == Action.WARN else None
            )
        
        return ToolCall(tool=tool.name, parameters=parameters)
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        tool = self.registry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        try:
            return tool.handler(**parameters)
        except TypeError as e:
            return f"Error: Invalid parameters - {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def execute_tool_call(self, tool_call: ToolCall) -> Any:
        return self.execute_tool(tool_call.tool, tool_call.parameters)
    
    def _extract_parameters(self, tool: Tool, message: str) -> Dict[str, Any]:
        return {"raw_input": message}
    
    def _extract_with_extractor(self, tool: Tool, message: str, extractor: Callable) -> Dict[str, Any]:
        return extractor(message, tool.parameters)
