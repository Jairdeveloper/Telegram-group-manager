from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field
import re


@dataclass
class GuardrailResult:
    allowed: bool
    filtered_content: Optional[str]
    reason: Optional[str]
    rule_triggered: Optional[str]
    matches: List[Dict[str, Any]] = field(default_factory=list)


class Guardrails:
    def __init__(self, name: str = "default"):
        self.name = name
        self._blocked_patterns: List[Tuple[re.Pattern, str]] = []
        self._allowed_patterns: List[re.Pattern] = []
        self._blocked_keywords: List[str] = []
    
    def add_blocked_pattern(self, pattern: str, description: str) -> None:
        compiled = re.compile(pattern, re.IGNORECASE)
        self._blocked_patterns.append((compiled, description))
    
    def add_blocked_keyword(self, keyword: str) -> None:
        self._blocked_keywords.append(keyword.lower())
    
    def add_allowed_pattern(self, pattern: str) -> None:
        compiled = re.compile(pattern, re.IGNORECASE)
        self._allowed_patterns.append(compiled)
    
    def remove_blocked_pattern(self, description: str) -> bool:
        for i, (pattern, desc) in enumerate(self._blocked_patterns):
            if desc == description:
                self._blocked_patterns.pop(i)
                return True
        return False
    
    def clear_patterns(self) -> None:
        self._blocked_patterns.clear()
        self._allowed_patterns.clear()
        self._blocked_keywords.clear()
    
    def check(self, content: str) -> GuardrailResult:
        matches = []
        
        for pattern, description in self._blocked_patterns:
            for match in pattern.finditer(content):
                matches.append({
                    "type": "pattern",
                    "description": description,
                    "match": match.group(),
                    "start": match.start(),
                    "end": match.end()
                })
        
        for keyword in self._blocked_keywords:
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            for match in pattern.finditer(content):
                matches.append({
                    "type": "keyword",
                    "description": "blocked_keyword",
                    "match": match.group(),
                    "start": match.start(),
                    "end": match.end()
                })
        
        if matches:
            return GuardrailResult(
                allowed=False,
                filtered_content=None,
                reason=f"Content matches blocked patterns: {', '.join(set(m['description'] for m in matches))}",
                rule_triggered=matches[0]["description"] if matches else None,
                matches=matches
            )
        
        if self._allowed_patterns:
            if not any(p.search(content) for p in self._allowed_patterns):
                return GuardrailResult(
                    allowed=False,
                    filtered_content=None,
                    reason="Content does not match allowed patterns",
                    rule_triggered="allowed_pattern",
                    matches=[]
                )
        
        return GuardrailResult(
            allowed=True,
            filtered_content=content,
            reason=None,
            rule_triggered=None,
            matches=[]
        )
    
    def filter(self, content: str, mask_char: str = "*") -> str:
        result = content
        
        for pattern, description in self._blocked_patterns:
            if pattern.search(result):
                result = pattern.sub(mask_char * 10, result)
        
        for keyword in self._blocked_keywords:
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            if pattern.search(result):
                result = pattern.sub(mask_char * len(keyword), result)
        
        return result
    
    def filter_specific(self, content: str, description: str, mask_char: str = "*") -> str:
        for pattern, desc in self._blocked_patterns:
            if desc == description and pattern.search(content):
                return pattern.sub(mask_char * 10, content)
        return content
    
    def list_blocked_patterns(self) -> List[str]:
        return [desc for _, desc in self._blocked_patterns]
    
    def list_blocked_keywords(self) -> List[str]:
        return self._blocked_keywords.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "blocked_patterns_count": len(self._blocked_patterns),
            "allowed_patterns_count": len(self._allowed_patterns),
            "blocked_keywords_count": len(self._blocked_keywords),
            "blocked_patterns": self.list_blocked_patterns(),
            "blocked_keywords": self.list_blocked_keywords()
        }
