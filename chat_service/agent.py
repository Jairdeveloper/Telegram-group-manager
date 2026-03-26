from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .pattern_engine import PatternEngine, Tokenizer, PronounTranslator
from app.config.settings import load_api_settings
from chat_service.llm.factory import LLMFactory, config_from_settings
from chat_service.llm.base import LLMError


@dataclass
class Response:
    text: str
    confidence: float = 1.0
    pattern_matched: bool = False
    source: str = "default"
    metadata: dict = field(default_factory=dict)


class Agent:
    """Orquestador/Agent: procesa entrada, matchea patrones y genera respuestas"""

    def __init__(
        self,
        pattern_responses: List[Tuple[List, List]],
        default_responses: List[List[str]],
        llm_enabled: Optional[bool] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
    ):
        self.pattern_responses = pattern_responses
        self.default_responses = default_responses

        self.pattern_engine = PatternEngine()
        self.pronoun_translator = PronounTranslator()
        self.tokenizer = Tokenizer()

        self.username = ""
        self.username_tag = "Username"
        self.default_response_index = 0
        settings = load_api_settings()
        self.llm_enabled = settings.llm_enabled if llm_enabled is None else llm_enabled
        self.llm_config = config_from_settings(
            settings,
            provider=llm_provider,
            model=llm_model,
        )

    def process(self, user_input: str) -> Response:
        tokens = self.tokenizer.tokenize(user_input)
        input_text = self.tokenizer.detokenize(tokens)

        matched_pattern = None
        binding_list = None
        response_template = None

        for pattern, response_tmpl in self.pattern_responses:
            bl = self.pattern_engine.match(pattern, input_text)
            if bl is not None:
                matched_pattern = pattern
                binding_list = bl
                response_template = response_tmpl
                break

        if binding_list is None:
            llm_text = self._generate_llm_response(input_text)
            if llm_text:
                return Response(
                    text=llm_text,
                    confidence=0.7,
                    pattern_matched=False,
                    source="llm",
                )
            response = self._generate_default_response()
            response.source = "default"
        else:
            translated_bindings = self.pronoun_translator.translate(binding_list)
            response_text = self._build_reply(response_template, translated_bindings)
            response = Response(
                text=response_text,
                confidence=0.9,
                pattern_matched=True,
                source="pattern",
                metadata={"pattern": matched_pattern, "bindings": translated_bindings},
            )

        return response

    def _generate_default_response(self) -> Response:
        resp = self.default_responses[self.default_response_index]
        text = " ".join(resp)
        self.default_response_index = (self.default_response_index + 1) % len(self.default_responses)
        return Response(text=text, source="default")

    def _build_reply(self, response_template: List, binding_list: List[List[str]]) -> str:
        binding_dict = {}

        for binding in binding_list:
            if isinstance(binding, list) and len(binding) > 0:
                key = binding[0]
                values = binding[1:]

                if key == self.username_tag and values:
                    if self.username and self.username != values[0]:
                        response = [values[0], "eh?", "what", "ever", "happened", "to", self.username]
                        return " ".join(response)
                    self.username = values[0]

                binding_dict[key] = values

        reply = []
        for elem in response_template:
            if isinstance(elem, list) and len(elem) > 1:
                binding_key = elem[1]
                if binding_key in binding_dict:
                    reply.extend(binding_dict[binding_key])
            else:
                reply.append(str(elem))

        return " ".join(reply)

    def _generate_llm_response(self, prompt: str) -> Optional[str]:
        if not self.llm_enabled:
            return None
        try:
            provider = LLMFactory.get_provider(self.llm_config)
            return provider.generate(prompt)
        except LLMError:
            return None
