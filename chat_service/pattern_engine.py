import re
from dataclasses import dataclass
from typing import Any, List, Dict, Optional


@dataclass
class Pattern:
    tokens: List[Any]
    regex: re.Pattern
    used_backrefs: List[str]


class PatternEngine:
    """Motor de reconocimiento de patrones"""

    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self.pattern_cache: Dict[tuple, Pattern] = {}

    def compile_pattern(self, pattern: List[Any]) -> Pattern:
        key = tuple(str(p) for p in pattern)
        if key in self.pattern_cache:
            return self.pattern_cache[key]

        regex = self._build_regex(pattern)
        used_backrefs = self._extract_backrefs(pattern)

        compiled = Pattern(tokens=pattern, regex=regex, used_backrefs=used_backrefs)
        self.pattern_cache[key] = compiled
        return compiled

    def _build_regex(self, pattern: List[Any]) -> re.Pattern:
        r = ["^"]
        used_backrefs = []

        for tok in pattern:
            if isinstance(tok, str):
                r.append(f"({re.escape(tok)})")
            elif isinstance(tok, int):
                if tok == 0:
                    r.append(r"[a-zA-Z ]*?")
                elif tok == 1:
                    r.append(r"[a-zA-Z]+")
            elif isinstance(tok, list) and len(tok) >= 2:
                bind_type, bind_name = tok[0], tok[1]
                if bind_name not in used_backrefs:
                    used_backrefs.append(bind_name)
                    if bind_type == 0:
                        r.append(f"(?P<{bind_name}>[a-zA-Z ]*?)")
                    elif bind_type == 1:
                        r.append(f"(?P<{bind_name}>[a-zA-Z]+)")

        regex_str = r"(\s)*".join(r) + r"$(\s)*"
        return re.compile(regex_str, re.IGNORECASE)

    def _extract_backrefs(self, pattern: List[Any]) -> List[str]:
        backrefs = []
        for tok in pattern:
            if isinstance(tok, list) and len(tok) >= 2:
                backrefs.append(tok[1])
        return backrefs

    def match(self, pattern: List[Any], sentence: str) -> Optional[List[List[str]]]:
        compiled = self.compile_pattern(pattern)
        matches = compiled.regex.search(sentence)

        if not matches:
            return None

        binding_list = []
        groups = matches.groups()

        for key, idx in compiled.regex.groupindex.items():
            group_value = groups[idx - 1].strip()
            if group_value:
                binding = [key, *group_value.split()]
                binding_list.append(binding)

        return binding_list


class Tokenizer:
    @staticmethod
    def tokenize(text: str) -> List[str]:
        return text.lower().strip().replace("(", "").replace(")", "").split()

    @staticmethod
    def detokenize(tokens: List[str]) -> str:
        return " ".join(tokens)


class PronounTranslator:
    DEFAULT_PRONOUN_MAP = {
        "i": "you", "you": "i", "my": "your", "me": "you", "your": "my",
        "i've": "you've", "we've": "they've",
        "fred": "he", "jack": "he", "jane": "she",
    }

    def __init__(self, custom_map: Optional[Dict[str, str]] = None):
        self.pronoun_map = {**self.DEFAULT_PRONOUN_MAP}
        if custom_map:
            self.pronoun_map.update(custom_map)

    def translate(self, binding_list: List[List[str]]) -> List[List[str]]:
        result = []
        for binding in binding_list:
            if isinstance(binding, list):
                translated = [binding[0]]
                for word in binding[1:]:
                    translated.append(self.pronoun_map.get(word.lower(), word))
                result.append(translated)
            else:
                result.append(binding)
        return result
