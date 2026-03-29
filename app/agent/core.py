from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import logging

from app.config.settings import load_api_settings
from app.ops.chat_integration import ChatContext, ChatService
from app.agent.context import ContextBuilder
from app.agent.memory import MemorySystem
from app.agent.rag import RAGService
from app.agent.reasoning import ReActReasoner, ReasoningAction
from app.agent.planner import AgentPlanner
from app.agent.actions import (
    ActionContext as AgentActionContext,
    ActionExecutor,
    ActionParser,
    SlotResolver,
    get_default_registry,
)
from app.monitoring.agent_metrics import (
    record_agent_action,
    record_agent_thought,
    record_llm_usage,
)
from chat_service.llm.factory import LLMFactory, config_from_settings
from chat_service.llm.base import LLMError

logger = logging.getLogger(__name__)


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
        nlp_enabled: Optional[bool] = None,
        nlp_min_confidence: Optional[float] = None,
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
        self.actions_enabled = settings.agent_actions_enabled
        self.action_registry = get_default_registry() if self.actions_enabled else None
        self.action_executor = (
            ActionExecutor(self.action_registry) if self.actions_enabled else None
        )
        self.action_parser = ActionParser() if self.actions_enabled else None
        self.slot_resolver = SlotResolver() if self.actions_enabled else None
        
        self.nlp_enabled = settings.nlp_enabled if nlp_enabled is None else nlp_enabled
        self.nlp_min_confidence = settings.nlp_min_confidence if nlp_min_confidence is None else nlp_min_confidence
        self._nlp_integration = None
        
        if self.nlp_enabled:
            logger.info("NLP integration enabled")
            self._init_nlp_integration()

    def _init_nlp_integration(self):
        try:
            from app.nlp import NLPBotIntegration
            from app.nlp.pipeline import PipelineConfig
            from app.config.settings import load_api_settings
            settings = load_api_settings()
            config = PipelineConfig(
                enable_llm_fallback=settings.nlp_llm_fallback,
                min_confidence_threshold=self.nlp_min_confidence
            )
            self._nlp_integration = NLPBotIntegration(
                config=config,
                min_confidence=self.nlp_min_confidence
            )
            logger.info("NLP integration initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize NLP integration: {e}")
            self._nlp_integration = None

    @property
    def nlp_integration(self):
        return self._nlp_integration

    def process(self, message: str, context: AgentContext) -> AgentResponse:
        message = (message or "").strip()
        tenant_id = context.tenant_id
        session_id = str(context.chat_id)
        context_window = self.context_builder.build(tenant_id=tenant_id, session_id=session_id)
        rendered_context = context_window.render()
        
        if self.nlp_enabled and self.nlp_integration:
            nlp_response = self._process_nlp(message, context)
            if nlp_response:
                return nlp_response
        
        if self.react_enabled:
            react_response = self._process_react(message, rendered_context, context)
            if react_response:
                return react_response
        if self.actions_enabled and self.action_parser and self.action_executor:
            action_response = self._process_actions_sync(message, context)
            if action_response:
                return action_response
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

    async def process_async(self, message: str, context: AgentContext) -> AgentResponse:
        message = (message or "").strip()
        tenant_id = context.tenant_id
        session_id = str(context.chat_id)
        context_window = self.context_builder.build(tenant_id=tenant_id, session_id=session_id)
        rendered_context = context_window.render()
        
        if self.nlp_enabled and self.nlp_integration:
            nlp_response = self._process_nlp(message, context)
            if nlp_response:
                return nlp_response
        
        if self.react_enabled:
            react_response = self._process_react(message, rendered_context, context)
            if react_response:
                return react_response
        if self.actions_enabled and self.action_parser and self.action_executor:
            action_response = await self._process_actions_async(message, context)
            if action_response:
                return action_response
        # Fallback to sync implementation for remaining paths
        return self.process(message, context)

    def _process_actions_sync(self, message: str, context: AgentContext) -> Optional[AgentResponse]:
        # Avoid blocking if no running loop available for async actions.
        return None

    def _process_nlp(self, message: str, context: AgentContext) -> Optional[AgentResponse]:
        if not self.nlp_integration:
            return None
        
        try:
            should_use = self.nlp_integration.should_use_nlp(message)
            if not should_use:
                logger.debug(f"NLP: message not classified as NLP command: {message}")
                return None
            
            result = self.nlp_integration.process_message(message)
            if not result or not result.action_result.action_id:
                logger.debug(f"NLP: no action result for: {message}")
                return None
            
            action_result = result.action_result
            logger.info(f"NLP: detected action {action_result.action_id} (confidence: {action_result.confidence})")
            
            action_def = self.action_registry.get(action_result.action_id) if self.action_registry else None
            if not action_def:
                logger.debug(f"NLP: action {action_result.action_id} not found in registry")
                return None
            
            resolution = self.slot_resolver.missing(action_def.schema, action_result.payload) if self.slot_resolver else None
            if resolution and resolution.missing_fields:
                return AgentResponse(
                    response=resolution.prompt,
                    source="nlp_slots",
                    metadata={
                        "action_id": action_result.action_id,
                        "missing_fields": resolution.missing_fields,
                        "nlp_confidence": action_result.confidence,
                    },
                )
            
            roles = []
            if context.metadata and isinstance(context.metadata, dict):
                roles = context.metadata.get("roles", []) or []
            
            action_context = AgentActionContext(
                chat_id=context.chat_id,
                tenant_id=context.tenant_id,
                user_id=int(context.user_id) if context.user_id else None,
                roles=roles,
            )
            
            import asyncio
            if asyncio.get_event_loop().is_running():
                result_sync = asyncio.create_task(
                    self.action_executor.execute(
                        action_result.action_id,
                        action_context,
                        action_result.payload,
                    )
                )
            else:
                result_sync = self.action_executor.execute(
                    action_result.action_id,
                    action_context,
                    action_result.payload,
                )
            
            if asyncio.iscoroutine(result_sync):
                return None
            
            response_text = result_sync.message or "Accion ejecutada."
            self.memory.add_exchange(
                tenant_id=context.tenant_id,
                session_id=str(context.chat_id),
                user_message=message,
                bot_response=response_text,
                metadata={
                    "source": "nlp_action",
                    "action_id": action_result.action_id,
                    "nlp_confidence": action_result.confidence,
                    "status": result_sync.status,
                },
            )
            return AgentResponse(
                response=response_text,
                source="nlp_action",
                metadata={
                    "action_id": action_result.action_id,
                    "nlp_confidence": action_result.confidence,
                    "status": result_sync.status,
                    "data": result_sync.data,
                },
            )
        except Exception as e:
            logger.error(f"NLP processing error: {e}")
            return None

    async def _process_actions_async(
        self,
        message: str,
        context: AgentContext,
    ) -> Optional[AgentResponse]:
        decision = self.action_parser.parse(message)
        if not decision.action_id:
            return None
        action_def = self.action_registry.get(decision.action_id)
        resolution = self.slot_resolver.missing(action_def.schema, decision.payload)
        if resolution.missing_fields:
            return AgentResponse(
                response=resolution.prompt,
                source="action_slots",
                metadata={
                    "action_id": decision.action_id,
                    "missing_fields": resolution.missing_fields,
                },
            )
        roles = []
        if context.metadata and isinstance(context.metadata, dict):
            roles = context.metadata.get("roles", []) or []
        action_context = AgentActionContext(
            chat_id=context.chat_id,
            tenant_id=context.tenant_id,
            user_id=int(context.user_id) if context.user_id else None,
            roles=roles,
        )
        result = await self.action_executor.execute(
            decision.action_id,
            action_context,
            decision.payload,
        )
        response_text = result.message or "Accion ejecutada."
        self.memory.add_exchange(
            tenant_id=context.tenant_id,
            session_id=str(context.chat_id),
            user_message=message,
            bot_response=response_text,
            metadata={
                "source": "action",
                "action_id": decision.action_id,
                "status": result.status,
            },
        )
        return AgentResponse(
            response=response_text,
            source="action",
            metadata={
                "action_id": decision.action_id,
                "status": result.status,
                "data": result.data,
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
