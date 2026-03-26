from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
import time
from app.monitoring.agent_metrics import record_tool_execution
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
        start = time.time()
        try:
            return tool.handler(**parameters)
        except TypeError as e:
            return f"Error: Invalid parameters - {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            record_tool_execution(tool_name, time.time() - start)
    
    def execute_tool_call(self, tool_call: ToolCall) -> Any:
        return self.execute_tool(tool_call.tool, tool_call.parameters)
    
    def _extract_parameters(self, tool: Tool, message: str) -> Dict[str, Any]:
        params = {}
        tool_params = tool.parameters
        
        clean_message = message.lower()
        for name in ['calculator', 'calculate', 'search', 'search for', 'convert', 'weather', 'database', 'db', 'http', 'fetch', 'get']:
            if clean_message.startswith(name + ' '):
                clean_message = clean_message[len(name):].strip()
                break
        
        for param_name, param_type in tool_params.items():
            if param_name == "expression" or param_name == "query" or param_name == "prompt":
                params[param_name] = clean_message if clean_message else message
            elif param_name in ["location", "value", "action", "url"]:
                words = message.split()
                for word in words:
                    if word.lower() not in [tool.name, 'calculate', 'search', 'for', 'convert', 'weather', 'database', 'db', 'http', 'fetch', 'get', 'the', 'web']:
                        params[param_name] = word
                        break
                if param_name not in params:
                    params[param_name] = clean_message if clean_message else message
        
        if not params:
            params = {"raw_input": message}
        
        return params
    
    def _extract_with_extractor(self, tool: Tool, message: str, extractor: Callable) -> Dict[str, Any]:
        return extractor(message, tool.parameters)
