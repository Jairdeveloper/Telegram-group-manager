"""Command processors for OPS and Enterprise commands."""

import logging
from typing import Any, Dict

from app.manager_bot._menu_service import get_menu_engine
from app.ops.events import record_event

from .base import MessageProcessor, ProcessorResult


logger = logging.getLogger(__name__)


class OpsCommandProcessor(MessageProcessor):
    """Processor for OPS commands."""

    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self.telegram_client = context.get("telegram_client")
        self.logger = context.get("logger")
        self.handle_ops_command_fn = context.get("handle_ops_command_fn")
        self.is_admin_fn = context.get("is_admin_fn")
        self.rate_limit_check = context.get("rate_limit_check")

    async def process(
        self,
        dispatch: Any,
        context: Dict[str, Any],
    ) -> ProcessorResult:
        """Process an OPS command."""
        update_id = dispatch.update_id
        chat_id = dispatch.chat_id
        command = dispatch.command
        args = dispatch.args

        result = await self.handle_ops_command_fn(
            chat_id,
            command or "",
            args,
            is_admin_fn=self.is_admin_fn,
            rate_limit_check=self.rate_limit_check,
        )

        reply = result.get("response_text", "(no response)")

        record_event(
            component="webhook",
            event="webhook.ops_service.ok",
            update_id=update_id,
            chat_id=chat_id,
            command=command,
            ops_status=result.get("status"),
            reply_len=len(reply or ""),
        )

        return ProcessorResult(reply=reply)


class EnterpriseCommandProcessor(MessageProcessor):
    """Processor for Enterprise commands."""

    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self.telegram_client = context.get("telegram_client")
        self.logger = context.get("logger")
        self.handle_enterprise_command_fn = context.get("handle_enterprise_command_fn")
        self.handle_enterprise_moderation_fn = context.get("handle_enterprise_moderation_fn")

    async def process(
        self,
        dispatch: Any,
        context: Dict[str, Any],
    ) -> ProcessorResult:
        """Process an Enterprise command."""
        update_id = dispatch.update_id
        chat_id = dispatch.chat_id
        user_id = dispatch.user_id
        command = dispatch.command
        args = dispatch.args
        text = dispatch.text
        raw_update = dispatch.raw_update

        logger.info(f"Enterprise command: {command}")

        result = self.handle_enterprise_command_fn(
            actor_id=user_id,
            chat_id=chat_id,
            command=command or "",
            args=args,
            raw_text=text or "",
            raw_update=raw_update,
        )

        logger.info(f"Enterprise result: {result}")

        if result.get("status") == "menu":
            menu_engine = get_menu_engine()
            menu_id = result.get("menu_id", "main")
            if menu_engine and self.telegram_client:
                await menu_engine.send_menu_message(
                    chat_id=chat_id,
                    bot=self.telegram_client,
                    menu_id=menu_id,
                )
                record_event(
                    component="webhook",
                    event="webhook.menu.display",
                    update_id=update_id,
                    chat_id=chat_id,
                    menu_id=menu_id,
                )
                return ProcessorResult()

        reply = result.get("response_text", "(no response)")

        record_event(
            component="webhook",
            event="webhook.enterprise_service.ok",
            update_id=update_id,
            chat_id=chat_id,
            command=command,
            enterprise_status=result.get("status"),
            reply_len=len(reply or ""),
        )

        return ProcessorResult(reply=reply)
