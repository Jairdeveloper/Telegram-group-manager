"""Chat message processor."""

import logging
from typing import Any, Dict, Optional

from app.agent.actions import ActionParser, ActionExecutor
from app.agent.actions.registry import get_default_registry
from app.agent.actions.types import ActionContext as AgentActionContext
from app.manager_bot._menu_service import get_conversation_state
from app.ops.services import handle_chat_message
from app.ops.events import record_event

from .base import MessageProcessor, ProcessorResult


logger = logging.getLogger(__name__)


class ChatMessageProcessor(MessageProcessor):
    """Processor for chat messages and agent tasks."""

    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self.telegram_client = context.get("telegram_client")
        self.logger = context.get("logger")
        self.handle_chat_message_fn = context.get("handle_chat_message_fn", handle_chat_message)
        self.handle_enterprise_moderation_fn = context.get("handle_enterprise_moderation_fn")

    async def process(
        self,
        dispatch: Any,
        context: Dict[str, Any],
    ) -> ProcessorResult:
        """Process a chat message."""
        from app.webhook.state import get_conversation_state_manager
        
        update_id = dispatch.update_id
        chat_id = dispatch.chat_id
        user_id = dispatch.user_id
        text = dispatch.text

        conversation = get_conversation_state()
        state = conversation.get_state(user_id, chat_id)

        if state:
            state_manager = get_conversation_state_manager()
            result = await state_manager.process(
                state=state,
                dispatch=dispatch,
                user_id=user_id,
                chat_id=chat_id,
            )
            if result:
                return result

        return await self._handle_regular_message(
            dispatch=dispatch,
            text=text,
            user_id=user_id,
            chat_id=chat_id,
            update_id=update_id,
        )

    async def _handle_regular_message(
        self,
        dispatch: Any,
        text: str,
        user_id: Optional[int],
        chat_id: int,
        update_id: int,
    ) -> ProcessorResult:
        """Handle regular message processing with ActionParser and NLP."""
        action_reply = None
        action_executed = False
        action_result = None

        try:
            parser = ActionParser(llm_enabled=True)
            parse_result = parser.parse(text or "")
            logger.info(f"ActionParser: text={text!r}, result={parse_result.action_id}, conf={parse_result.confidence}")

            if parse_result.action_id and parse_result.confidence >= 0.5:
                user_roles = ["admin"]
                executor = ActionExecutor(get_default_registry())
                action_context = AgentActionContext(
                    chat_id=chat_id,
                    tenant_id="default",
                    user_id=user_id,
                    roles=user_roles,
                )
                action_result = await executor.execute(
                    parse_result.action_id,
                    action_context,
                    parse_result.payload,
                )
                logger.info(f"ActionParser: action_result status={action_result.status}, message={action_result.message}")
                action_reply = action_result.message
                action_executed = True
                record_event(
                    component="webhook",
                    event="webhook.action_parser.executed",
                    update_id=update_id,
                    chat_id=chat_id,
                    action_id=parse_result.action_id,
                    confidence=parse_result.confidence,
                    status=action_result.status,
                )
        except Exception as e:
            logger.error(f"ActionParser failed: {e}", exc_info=True)
            action_reply = None
            action_executed = False

        if action_executed and action_result and action_result.status == "ok" and action_reply:
            return ProcessorResult(reply=action_reply)

        if action_executed and action_result and action_result.status != "ok":
            reply = action_result.response_text or f"La acción falló: {action_result.status}"
            record_event(
                component="webhook",
                event="webhook.action_failed",
                update_id=update_id,
                chat_id=chat_id,
                action_status=action_result.status,
                reply_len=len(reply or ""),
            )
            return ProcessorResult(reply=reply)

        return await self._handle_service_fallback(
            dispatch=dispatch,
            text=text,
            chat_id=chat_id,
            update_id=update_id,
        )

    async def _handle_service_fallback(
        self,
        dispatch: Any,
        text: str,
        chat_id: int,
        update_id: int,
    ) -> ProcessorResult:
        """Handle service fallback (NLP/Chat service)."""
        from app.nlp.integration import get_nlp_integration
        import traceback

        # Check enterprise moderation first
        if self.handle_enterprise_moderation_fn:
            try:
                moderation_result = self.handle_enterprise_moderation_fn(
                    actor_id=dispatch.user_id,
                    chat_id=chat_id,
                    raw_text=text,
                    raw_update=dispatch.raw_update,
                )
                if moderation_result.get("status") == "blocked":
                    record_event(
                        component="webhook",
                        event="webhook.moderation.blocked",
                        update_id=update_id,
                        chat_id=chat_id,
                        reason=moderation_result.get("reason"),
                    )
                    return ProcessorResult(
                        reply=moderation_result.get("response_text", "Mensaje bloqueado."),
                        skip_send=False,
                    )
            except Exception as mod_error:
                logger.error(f"Moderation check failed: {mod_error}\n{traceback.format_exc()}")

        try:
            nlp_integration = get_nlp_integration()

            if text and nlp_integration.should_use_nlp(text):
                nlp_result = nlp_integration.process_message(text)
                if (nlp_result and
                    hasattr(nlp_result, 'action_result') and
                    nlp_result.action_result and
                    nlp_result.action_result.action_id):
                    reply = f"✓ Accion: {nlp_result.action_result.action_id}"
                    record_event(
                        component="webhook",
                        event="webhook.nlp_flow.ok",
                        update_id=update_id,
                        chat_id=chat_id,
                        action_id=nlp_result.action_result.action_id,
                        confidence=nlp_result.action_result.confidence,
                        intent=nlp_result.intent,
                    )
                    return ProcessorResult(reply=reply)
                else:
                    result = self.handle_chat_message_fn(chat_id, text)
                    if result and isinstance(result, dict):
                        reply = result.get("response", "(no response)")
                    else:
                        reply = "(no response)"
                        logger.warning(f"Invalid result from handle_chat_message_fn: {result}")
                    record_event(
                        component="webhook",
                        event="webhook.chat_service.ok",
                        update_id=update_id,
                        chat_id=chat_id,
                        reply_len=len(reply or ""),
                        nlp_intent=nlp_result.intent if nlp_result else None,
                    )
                    return ProcessorResult(reply=reply)
            else:
                result = self.handle_chat_message_fn(chat_id, text)
                if result and isinstance(result, dict):
                    reply = result.get("response", "(no response)")
                else:
                    reply = "(no response)"
                    logger.warning(f"Invalid result from handle_chat_message_fn in fallback: {result}")
                record_event(
                    component="webhook",
                    event="webhook.chat_service.ok",
                    update_id=update_id,
                    chat_id=chat_id,
                    reply_len=len(reply or ""),
                )
                return ProcessorResult(reply=reply)
        except Exception as e:
            import traceback
            logger.error(f"🔴 CRITICAL NLP PROCESSING ERROR: {type(e).__name__}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            logger.error(f"Falling back to chat service for chat_id={chat_id}, text='{text}'")
            result = self.handle_chat_message_fn(chat_id, text)
            if result and isinstance(result, dict):
                reply = result.get("response", "(no response)")
            else:
                reply = "(no response)"
                logger.error(f"handle_chat_message_fn failed to return valid result: {result}")
            record_event(
                component="webhook",
                event="webhook.chat_service.fallback",
                update_id=update_id,
                chat_id=chat_id,
                error=str(e),
                error_type=type(e).__name__,
                reply_len=len(reply or ""),
            )
            return ProcessorResult(reply=reply)
