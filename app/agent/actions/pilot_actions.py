from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.manager_bot.services import GroupConfigService

from .registry import ActionDefinition, ActionRegistry
from .types import ActionContext, ActionResult


class WelcomeToggleParams(BaseModel):
    enabled: bool = Field(..., description="Enable or disable welcome messages")


class WelcomeSetTextParams(BaseModel):
    text: str = Field(..., min_length=1, max_length=2048, description="Welcome text")


class AntispamToggleParams(BaseModel):
    enabled: bool = Field(..., description="Enable or disable antispam")


async def _welcome_toggle(ctx: ActionContext, params: WelcomeToggleParams) -> ActionResult:
    service = GroupConfigService()
    config = await service.update(
        chat_id=ctx.chat_id,
        tenant_id=ctx.tenant_id,
        updated_by=ctx.user_id,
        updater=lambda cfg: setattr(cfg, "welcome_enabled", params.enabled),
    )
    return ActionResult(
        status="ok",
        message="Welcome actualizado",
        data={"welcome_enabled": config.welcome_enabled},
    )


async def _welcome_set_text(ctx: ActionContext, params: WelcomeSetTextParams) -> ActionResult:
    service = GroupConfigService()

    def _apply(cfg):
        cfg.welcome_text = params.text
        if not cfg.welcome_enabled:
            cfg.welcome_enabled = True

    config = await service.update(
        chat_id=ctx.chat_id,
        tenant_id=ctx.tenant_id,
        updated_by=ctx.user_id,
        updater=_apply,
    )
    return ActionResult(
        status="ok",
        message="Welcome actualizado",
        data={"welcome_text": config.welcome_text, "welcome_enabled": config.welcome_enabled},
    )


async def _antispam_toggle(ctx: ActionContext, params: AntispamToggleParams) -> ActionResult:
    service = GroupConfigService()
    config = await service.update(
        chat_id=ctx.chat_id,
        tenant_id=ctx.tenant_id,
        updated_by=ctx.user_id,
        updater=lambda cfg: setattr(cfg, "antispam_enabled", params.enabled),
    )
    return ActionResult(
        status="ok",
        message="Antispam actualizado",
        data={"antispam_enabled": config.antispam_enabled},
    )


def register_pilot_actions(registry: ActionRegistry) -> None:
    registry.register(
        ActionDefinition(
            action_id="welcome.toggle",
            description="Activar o desactivar mensaje de bienvenida",
            schema=WelcomeToggleParams,
            permissions=("admin", "moderator"),
            execute=_welcome_toggle,
        )
    )
    registry.register(
        ActionDefinition(
            action_id="welcome.set_text",
            description="Actualizar texto de bienvenida",
            schema=WelcomeSetTextParams,
            permissions=("admin", "moderator"),
            execute=_welcome_set_text,
        )
    )
    registry.register(
        ActionDefinition(
            action_id="antispam.toggle",
            description="Activar o desactivar antispam",
            schema=AntispamToggleParams,
            permissions=("admin", "moderator"),
            execute=_antispam_toggle,
        )
    )
