from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ToolType(str, Enum):
    SEARCH = "search"
    CALCULATOR = "calculator"
    WEATHER = "weather"
    DATABASE = "database"
    HTTP = "http"
    CUSTOM = "custom"
    LLM = "llm"


@dataclass
class Tool:
    name: str
    description: str
    tool_type: ToolType
    handler: Callable
    parameters: Dict[str, Any]
    requires_approval: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool
    
    def unregister(self, name: str) -> Optional[Tool]:
        return self._tools.pop(name, None)
    
    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)
    
    def list_tools(self) -> List[Tool]:
        return list(self._tools.values())
    
    def list_tools_by_type(self, tool_type: ToolType) -> List[Tool]:
        return [t for t in self._tools.values() if t.tool_type == tool_type]
    
    def find_tools(self, query: str) -> List[Tool]:
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        results = []
        for t in self._tools.values():
            name_lower = t.name.lower()
            desc_lower = t.description.lower()
            
            if query_lower in name_lower or query_lower in desc_lower:
                results.append(t)
            elif any(word in name_lower or word in desc_lower for word in query_words):
                results.append(t)
        
        return results
    
    def tool_exists(self, name: str) -> bool:
        return name in self._tools
    
    def get_tool_names(self) -> List[str]:
        return list(self._tools.keys())
    
    def clear(self) -> None:
        self._tools.clear()
