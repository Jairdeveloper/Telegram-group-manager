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


async def _welcome_toggle_dry_run(ctx: ActionContext, params: WelcomeToggleParams) -> ActionResult:
    service = GroupConfigService()
    config = await service.get_or_create(chat_id=ctx.chat_id, tenant_id=ctx.tenant_id)
    return ActionResult(
        status="preview",
        message="Previsualizacion welcome.toggle",
        data={
            "current": config.welcome_enabled,
            "next": params.enabled,
        },
    )


async def _welcome_toggle_snapshot(ctx: ActionContext, params: WelcomeToggleParams):
    service = GroupConfigService()
    config = await service.get_or_create(chat_id=ctx.chat_id, tenant_id=ctx.tenant_id)
    return {"welcome_enabled": config.welcome_enabled}


async def _welcome_toggle_undo(ctx: ActionContext, params: WelcomeToggleParams, previous_state):
    service = GroupConfigService()
    config = await service.update(
        chat_id=ctx.chat_id,
        tenant_id=ctx.tenant_id,
        updated_by=ctx.user_id,
        updater=lambda cfg: setattr(cfg, "welcome_enabled", previous_state.get("welcome_enabled", False)),
    )
    return ActionResult(
        status="ok",
        message="Rollback welcome.toggle aplicado",
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


async def _welcome_set_text_dry_run(ctx: ActionContext, params: WelcomeSetTextParams) -> ActionResult:
    service = GroupConfigService()
    config = await service.get_or_create(chat_id=ctx.chat_id, tenant_id=ctx.tenant_id)
    return ActionResult(
        status="preview",
        message="Previsualizacion welcome.set_text",
        data={
            "current_text": config.welcome_text,
            "next_text": params.text,
            "will_enable": not config.welcome_enabled,
        },
    )


async def _welcome_set_text_snapshot(ctx: ActionContext, params: WelcomeSetTextParams):
    service = GroupConfigService()
    config = await service.get_or_create(chat_id=ctx.chat_id, tenant_id=ctx.tenant_id)
    return {
        "welcome_text": config.welcome_text,
        "welcome_enabled": config.welcome_enabled,
    }


async def _welcome_set_text_undo(ctx: ActionContext, params: WelcomeSetTextParams, previous_state):
    service = GroupConfigService()

    def _apply(cfg):
        cfg.welcome_text = previous_state.get("welcome_text", "")
        cfg.welcome_enabled = previous_state.get("welcome_enabled", False)

    config = await service.update(
        chat_id=ctx.chat_id,
        tenant_id=ctx.tenant_id,
        updated_by=ctx.user_id,
        updater=_apply,
    )
    return ActionResult(
        status="ok",
        message="Rollback welcome.set_text aplicado",
        data={
            "welcome_text": config.welcome_text,
            "welcome_enabled": config.welcome_enabled,
        },
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


async def _antispam_toggle_dry_run(ctx: ActionContext, params: AntispamToggleParams) -> ActionResult:
    service = GroupConfigService()
    config = await service.get_or_create(chat_id=ctx.chat_id, tenant_id=ctx.tenant_id)
    return ActionResult(
        status="preview",
        message="Previsualizacion antispam.toggle",
        data={
            "current": config.antispam_enabled,
            "next": params.enabled,
        },
    )


async def _antispam_toggle_snapshot(ctx: ActionContext, params: AntispamToggleParams):
    service = GroupConfigService()
    config = await service.get_or_create(chat_id=ctx.chat_id, tenant_id=ctx.tenant_id)
    return {"antispam_enabled": config.antispam_enabled}


async def _antispam_toggle_undo(ctx: ActionContext, params: AntispamToggleParams, previous_state):
    service = GroupConfigService()
    config = await service.update(
        chat_id=ctx.chat_id,
        tenant_id=ctx.tenant_id,
        updated_by=ctx.user_id,
        updater=lambda cfg: setattr(cfg, "antispam_enabled", previous_state.get("antispam_enabled", False)),
    )
    return ActionResult(
        status="ok",
        message="Rollback antispam.toggle aplicado",
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
            snapshot=_welcome_toggle_snapshot,
            undo=_welcome_toggle_undo,
            dry_run=_welcome_toggle_dry_run,
            requires_confirmation=False,
        )
    )
    registry.register(
        ActionDefinition(
            action_id="welcome.set_text",
            description="Actualizar texto de bienvenida",
            schema=WelcomeSetTextParams,
            permissions=("admin", "moderator"),
            execute=_welcome_set_text,
            snapshot=_welcome_set_text_snapshot,
            undo=_welcome_set_text_undo,
            dry_run=_welcome_set_text_dry_run,
            requires_confirmation=True,
        )
    )
    registry.register(
        ActionDefinition(
            action_id="antispam.toggle",
            description="Activar o desactivar antispam",
            schema=AntispamToggleParams,
            permissions=("admin", "moderator"),
            execute=_antispam_toggle,
            snapshot=_antispam_toggle_snapshot,
            undo=_antispam_toggle_undo,
            dry_run=_antispam_toggle_dry_run,
            requires_confirmation=False,
        )
    )
