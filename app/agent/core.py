from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from app.config.settings import load_api_settings
from app.ops.chat_integration import ChatContext, ChatService
from app.agent.context import ContextBuilder
from app.agent.memory import MemorySystem
from app.agent.rag import RAGService
from app.agent.reasoning import ReActReasoner, ReasoningAction
from app.agent.planner import AgentPlanner
from app.monitoring.agent_metrics import (
    record_agent_action,
    record_agent_thought,
    record_llm_usage,
)
from chat_service.llm.factory import LLMFactory, config_from_settings
from chat_service.llm.base import LLMError


@dataclass
class AgentContext:
    chat_id: int
    tenant_id: str = "default"
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    response: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentCore:
    def __init__(
        self,
        chat_service: Optional[ChatService] = None,
        memory: Optional[MemorySystem] = None,
        context_builder: Optional[ContextBuilder] = None,
        rag_service: Optional[RAGService] = None,
        reasoner: Optional[ReActReasoner] = None,
        planner: Optional[AgentPlanner] = None,
        llm_enabled: Optional[bool] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
    ):
        settings = load_api_settings()
        self.llm_enabled = settings.llm_enabled if llm_enabled is None else llm_enabled
        self.llm_config = config_from_settings(
            settings,
            provider=llm_provider,
            model=llm_model,
        )
        self.chat_service = chat_service or ChatService()
        self.memory = memory or MemorySystem()
        self.context_builder = context_builder or ContextBuilder(self.memory)
        self.rag_service = rag_service or RAGService()
        self.rag_enabled = settings.rag_enabled
        self.react_enabled = settings.agent_react_enabled
        self.max_iterations = settings.agent_max_iterations
        self.reasoner = reasoner or ReActReasoner()
        self.planner = planner or AgentPlanner()

    def process(self, message: str, context: AgentContext) -> AgentResponse:
        message = (message or "").strip()
        tenant_id = context.tenant_id
        session_id = str(context.chat_id)
        context_window = self.context_builder.build(tenant_id=tenant_id, session_id=session_id)
        rendered_context = context_window.render()
        if self.react_enabled:
            react_response = self._process_react(message, rendered_context, context)
            if react_response:
                return react_response
        if self.rag_enabled:
            docs = self.rag_service.search(message, tenant_id=tenant_id)
            if docs:
                rag_answer = self.rag_service.generate_with_context(message, docs)
                if rag_answer:
                    self.memory.add_exchange(
                        tenant_id=tenant_id,
                        session_id=session_id,
                        user_message=message,
                        bot_response=rag_answer,
                        metadata={"source": "rag"},
                    )
                    return AgentResponse(
                        response=rag_answer,
                        source="rag",
                        metadata={"docs": len(docs)},
                    )
        if self.llm_enabled:
            try:
                provider = LLMFactory.get_provider(self.llm_config)
                llm_text = provider.generate(
                    message,
                    system_prompt=rendered_context if rendered_context else None,
                )
                if llm_text:
                    record_llm_usage(
                        provider=self.llm_config.provider,
                        model=self.llm_config.model,
                        prompt=message,
                        response=llm_text,
                        source="agent",
                    )
                    self.memory.add_exchange(
                        tenant_id=tenant_id,
                        session_id=session_id,
                        user_message=message,
                        bot_response=llm_text,
                        metadata={"source": "llm"},
                    )
                    return AgentResponse(response=llm_text, source="llm")
            except LLMError:
                pass

        chat_context = ChatContext(
            chat_id=context.chat_id,
            tenant_id=context.tenant_id,
            user_id=context.user_id,
        )
        result = self.chat_service.handle_message(message, chat_context)
        self.memory.add_exchange(
            tenant_id=tenant_id,
            session_id=session_id,
            user_message=message,
            bot_response=result.response,
            metadata={"source": "planner", "plan_id": result.plan_id},
        )
        return AgentResponse(
            response=result.response,
            source="planner",
            metadata={
                "plan_id": result.plan_id,
                "tools_executed": result.tools_executed,
                "blocked": result.blocked,
            },
        )

    def _process_react(self, message: str, rendered_context: str, context: AgentContext) -> Optional[AgentResponse]:
        decision = self.reasoner.decide(message)
        thought = self.reasoner.think(message, rendered_context)
        record_agent_thought("react")
        if decision.action == ReasoningAction.RESPOND:
            record_agent_action("respond")
            if self.llm_enabled:
                try:
                    provider = LLMFactory.get_provider(self.llm_config)
                    response_text = provider.generate(
                        message,
                        system_prompt=rendered_context if rendered_context else None,
                    )
                    if response_text:
                        record_llm_usage(
                            provider=self.llm_config.provider,
                            model=self.llm_config.model,
                            prompt=message,
                            response=response_text,
                            source="react",
                        )
                        return AgentResponse(
                            response=response_text,
                            source="react",
                            metadata={"thought": thought, "action": "respond"},
                        )
                except LLMError:
                    return None
            return None

        record_agent_action("plan")
        plan = self.planner.create_plan(
            message,
            {"tenant_id": context.tenant_id, "chat_id": context.chat_id, "user_id": context.user_id},
        )
        executed = self.planner.execute_plan(plan.plan_id)
        final_result = executed.final_result or ""
        if self.llm_enabled and final_result:
            prompt = (
                "Usa los resultados de herramientas para responder al usuario.\n\n"
                f"Resultados: {final_result}\n\n"
                f"Pregunta: {message}"
            )
            try:
                provider = LLMFactory.get_provider(self.llm_config)
                response_text = provider.generate(prompt)
                if response_text:
                    record_llm_usage(
                        provider=self.llm_config.provider,
                        model=self.llm_config.model,
                        prompt=prompt,
                        response=response_text,
                        source="react",
                    )
                    return AgentResponse(
                        response=response_text,
                        source="react",
                        metadata={"thought": thought, "action": "plan", "plan_id": executed.plan_id},
                    )
            except LLMError:
                pass
        if final_result:
            return AgentResponse(
                response=final_result,
                source="react",
                metadata={"thought": thought, "action": "plan", "plan_id": executed.plan_id},
            )
        return None


_default_agent_core: Optional[AgentCore] = None


def get_default_agent_core() -> AgentCore:
    global _default_agent_core
    if _default_agent_core is None:
        _default_agent_core = AgentCore()
    return _default_agent_core
