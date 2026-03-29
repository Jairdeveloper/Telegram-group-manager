from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List

from pydantic import BaseModel, Field

from app.manager_bot.services import GroupConfigService
from app.enterprise.infrastructure.content_repositories import get_welcome_repo
from app.enterprise.domain.entities import EnterpriseWelcome

from .registry import ActionDefinition, ActionRegistry
from .types import ActionContext, ActionResult


class WelcomeToggleParams(BaseModel):
    enabled: bool = Field(..., description="Enable or disable welcome messages")


class WelcomeSetTextParams(BaseModel):
    text: str = Field(..., min_length=1, max_length=2048, description="Welcome text")


class CreativeWelcomeParams(BaseModel):
    pass


CREATIVE_WELCOME_MESSAGES = [
    "¡Bienvenido/a! 🎉 Nos alegra tenerte aquí. Este es un espacio para compartir y aprender juntos.",
    "¡Hola! 👋 Bienvenido/a a nuestro grupo. Esperamos que disfrutes tu estancia aquí.",
    "¡Bienvenido/a! 🚀 Este es un lugar donde la comunidad crece juntos. ¡Participa y aprende!",
    "¡Hola! 🌟 Gracias por unirte a nuestro grupo. Aquí encontrarás un espacio de colaboración.",
    "¡Bienvenido/a! 💫 Nos complace tenerte con nosotros. Comparte tus conocimientos y aprende de otros.",
]


class AntispamToggleParams(BaseModel):
    enabled: bool = Field(..., description="Enable or disable antispam")


async def _welcome_toggle(ctx: ActionContext, params: WelcomeToggleParams) -> ActionResult:
    welcome_repo = get_welcome_repo()
    existing = welcome_repo.get(ctx.tenant_id or "default", ctx.chat_id)
    welcome = EnterpriseWelcome(
        tenant_id=ctx.tenant_id or "default",
        chat_id=ctx.chat_id,
        welcome_text=existing.welcome_text if existing else "",
        enabled=params.enabled,
    )
    welcome = welcome_repo.set(welcome)
    return ActionResult(
        status="ok",
        message="Welcome actualizado",
        data={"welcome_enabled": welcome.enabled},
    )


async def _welcome_toggle_dry_run(ctx: ActionContext, params: WelcomeToggleParams) -> ActionResult:
    welcome_repo = get_welcome_repo()
    existing = welcome_repo.get(ctx.tenant_id or "default", ctx.chat_id)
    current = existing.enabled if existing else False
    return ActionResult(
        status="preview",
        message="Previsualizacion welcome.toggle",
        data={
            "current": current,
            "next": params.enabled,
        },
    )


async def _welcome_toggle_snapshot(ctx: ActionContext, params: WelcomeToggleParams):
    welcome_repo = get_welcome_repo()
    existing = welcome_repo.get(ctx.tenant_id or "default", ctx.chat_id)
    return {"welcome_enabled": existing.enabled if existing else False}


async def _welcome_toggle_undo(ctx: ActionContext, params: WelcomeToggleParams, previous_state):
    welcome_repo = get_welcome_repo()
    existing = welcome_repo.get(ctx.tenant_id or "default", ctx.chat_id)
    welcome = EnterpriseWelcome(
        tenant_id=ctx.tenant_id or "default",
        chat_id=ctx.chat_id,
        welcome_text=existing.welcome_text if existing else "",
        enabled=previous_state.get("welcome_enabled", False),
    )
    welcome = welcome_repo.set(welcome)
    return ActionResult(
        status="ok",
        message="Rollback welcome.toggle aplicado",
        data={"welcome_enabled": welcome.enabled},
    )


async def _welcome_set_text(ctx: ActionContext, params: WelcomeSetTextParams) -> ActionResult:
    welcome_repo = get_welcome_repo()
    existing = welcome_repo.get(ctx.tenant_id or "default", ctx.chat_id)
    welcome = EnterpriseWelcome(
        tenant_id=ctx.tenant_id or "default",
        chat_id=ctx.chat_id,
        welcome_text=params.text,
        enabled=existing.enabled if existing else True,
    )
    welcome = welcome_repo.set(welcome)
    # Verify it was saved
    saved = welcome_repo.get(ctx.tenant_id or "default", ctx.chat_id)
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Welcome saved: {saved.welcome_text if saved else 'NONE'}")
    return ActionResult(
        status="ok",
        message="Welcome actualizado",
        data={"welcome_text": welcome.welcome_text},
    )


import random


async def _welcome_set_creative_text(ctx: ActionContext, params: CreativeWelcomeParams) -> ActionResult:
    welcome_repo = get_welcome_repo()
    existing = welcome_repo.get(ctx.tenant_id or "default", ctx.chat_id)
    
    creative_message = random.choice(CREATIVE_WELCOME_MESSAGES)
    
    welcome = EnterpriseWelcome(
        tenant_id=ctx.tenant_id or "default",
        chat_id=ctx.chat_id,
        welcome_text=creative_message,
        enabled=True,
    )
    welcome = welcome_repo.set(welcome)
    
    return ActionResult(
        status="ok",
        message=f"✅ Mensaje de bienvenida configurado:\n\n{creative_message}",
        data={"welcome_text": creative_message, "welcome_enabled": True},
    )


async def _welcome_set_text_dry_run(ctx: ActionContext, params: WelcomeSetTextParams) -> ActionResult:
    welcome_repo = get_welcome_repo()
    existing = welcome_repo.get(ctx.tenant_id or "default", ctx.chat_id)
    return ActionResult(
        status="preview",
        message="Previsualizacion welcome.set_text",
        data={
            "current_text": existing.welcome_text if existing else "",
            "next_text": params.text,
            "will_enable": existing.enabled if existing else True,
        },
    )


async def _welcome_set_text_snapshot(ctx: ActionContext, params: WelcomeSetTextParams):
    welcome_repo = get_welcome_repo()
    existing = welcome_repo.get(ctx.tenant_id or "default", ctx.chat_id)
    return {
        "welcome_text": existing.welcome_text if existing else "",
        "welcome_enabled": existing.enabled if existing else False,
    }


async def _welcome_set_text_undo(ctx: ActionContext, params: WelcomeSetTextParams, previous_state):
    welcome_repo = get_welcome_repo()
    welcome = EnterpriseWelcome(
        tenant_id=ctx.tenant_id or "default",
        chat_id=ctx.chat_id,
        welcome_text=previous_state.get("welcome_text", ""),
        enabled=previous_state.get("welcome_enabled", False),
    )
    welcome = welcome_repo.set(welcome)
    return ActionResult(
        status="ok",
        message="Rollback welcome.set_text aplicado",
        data={"welcome_text": welcome.welcome_text, "welcome_enabled": welcome.enabled},
    )

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


class AntifloodToggleParams(BaseModel):
    enabled: bool = Field(..., description="Enable or disable antiflood")


class AntifloodSetLimitsParams(BaseModel):
    limit: int = Field(..., ge=1, le=100, description="Number of messages")
    interval: int = Field(..., ge=1, le=300, description="Time window in seconds")


class AntifloodSetActionParams(BaseModel):
    action: str = Field(..., description="Action: warn, mute, ban, kick")


class GoodbyeToggleParams(BaseModel):
    enabled: bool = Field(..., description="Enable or disable goodbye messages")


class GoodbyeSetTextParams(BaseModel):
    text: str = Field(..., min_length=1, max_length=2048, description="Goodbye text")


class FilterAddWordParams(BaseModel):
    word: str = Field(..., min_length=1, description="Word to block")


class FilterRemoveWordParams(BaseModel):
    word: str = Field(..., min_length=1, description="Word to unblock")


async def _antiflood_toggle(ctx: ActionContext, params: AntifloodToggleParams) -> ActionResult:
    service = GroupConfigService()
    config = await service.update(
        chat_id=ctx.chat_id,
        tenant_id=ctx.tenant_id,
        updated_by=ctx.user_id,
        updater=lambda cfg: setattr(cfg, "antiflood_enabled", params.enabled),
    )
    return ActionResult(
        status="ok",
        message="Antiflood actualizado",
        data={"antiflood_enabled": config.antiflood_enabled},
    )


async def _antiflood_set_limits(ctx: ActionContext, params: AntifloodSetLimitsParams) -> ActionResult:
    service = GroupConfigService()
    config = await service.update(
        chat_id=ctx.chat_id,
        tenant_id=ctx.tenant_id,
        updated_by=ctx.user_id,
        updater=lambda cfg: setattr(cfg, "antiflood_limit", params.limit) or setattr(cfg, "antiflood_interval", params.interval),
    )
    return ActionResult(
        status="ok",
        message=f"Antiflood configurado: {params.limit} mensajes en {params.interval} segundos",
        data={"antiflood_limit": config.antiflood_limit, "antiflood_interval": config.antiflood_interval},
    )


async def _antiflood_set_action(ctx: ActionContext, params: AntifloodSetActionParams) -> ActionResult:
    valid_actions = ("warn", "mute", "ban", "kick", "off")
    if params.action not in valid_actions:
        return ActionResult(
            status="error",
            message=f"Acción inválida. Usa: {', '.join(valid_actions)}",
            data={},
        )
    service = GroupConfigService()
    config = await service.update(
        chat_id=ctx.chat_id,
        tenant_id=ctx.tenant_id,
        updated_by=ctx.user_id,
        updater=lambda cfg: setattr(cfg, "antiflood_action", params.action),
    )
    return ActionResult(
        status="ok",
        message=f"Antiflood: acción configurada a '{params.action}'",
        data={"antiflood_action": config.antiflood_action},
    )


async def _goodbye_toggle(ctx: ActionContext, params: GoodbyeToggleParams) -> ActionResult:
    service = GroupConfigService()
    config = await service.update(
        chat_id=ctx.chat_id,
        tenant_id=ctx.tenant_id,
        updated_by=ctx.user_id,
        updater=lambda cfg: setattr(cfg, "goodbye_enabled", params.enabled),
    )
    return ActionResult(
        status="ok",
        message="Despedida actualizada",
        data={"goodbye_enabled": config.goodbye_enabled},
    )


async def _goodbye_set_text(ctx: ActionContext, params: GoodbyeSetTextParams) -> ActionResult:
    service = GroupConfigService()

    def _apply(cfg):
        cfg.goodbye_text = params.text
        if not cfg.goodbye_enabled:
            cfg.goodbye_enabled = True

    config = await service.update(
        chat_id=ctx.chat_id,
        tenant_id=ctx.tenant_id,
        updated_by=ctx.user_id,
        updater=_apply,
    )
    return ActionResult(
        status="ok",
        message="Texto de despedida actualizado",
        data={"goodbye_text": config.goodbye_text, "goodbye_enabled": config.goodbye_enabled},
    )


async def _filter_add_word(ctx: ActionContext, params: FilterAddWordParams) -> ActionResult:
    service = GroupConfigService()
    config = await service.update(
        chat_id=ctx.chat_id,
        tenant_id=ctx.tenant_id,
        updated_by=ctx.user_id,
        updater=lambda cfg: setattr(cfg, "blocked_words_enabled", True) or (
            cfg.blocked_words.append(params.word) if params.word not in cfg.blocked_words else None
        ),
    )
    return ActionResult(
        status="ok",
        message=f"Palabra '{params.word}' bloqueada",
        data={"blocked_words": config.blocked_words},
    )


async def _filter_remove_word(ctx: ActionContext, params: FilterRemoveWordParams) -> ActionResult:
    service = GroupConfigService()
    config = await service.update(
        chat_id=ctx.chat_id,
        tenant_id=ctx.tenant_id,
        updated_by=ctx.user_id,
        updater=lambda cfg: cfg.blocked_words.remove(params.word) if params.word in cfg.blocked_words else None,
    )
    return ActionResult(
        status="ok",
        message=f"Palabra '{params.word}' desbloqueada",
        data={"blocked_words": config.blocked_words},
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
            requires_confirmation=False,
        )
    )
    registry.register(
        ActionDefinition(
            action_id="welcome.set_creative_text",
            description="Generar mensaje de bienvenida automáticamente",
            schema=CreativeWelcomeParams,
            permissions=("admin", "moderator"),
            execute=_welcome_set_creative_text,
            requires_confirmation=False,
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
    registry.register(
        ActionDefinition(
            action_id="antiflood.toggle",
            description="Activar o desactivar antiflood",
            schema=AntifloodToggleParams,
            permissions=("admin", "moderator"),
            execute=_antiflood_toggle,
            requires_confirmation=False,
        )
    )
    registry.register(
        ActionDefinition(
            action_id="antiflood.set_limits",
            description="Configurar límites de antiflood",
            schema=AntifloodSetLimitsParams,
            permissions=("admin", "moderator"),
            execute=_antiflood_set_limits,
            requires_confirmation=False,
        )
    )
    registry.register(
        ActionDefinition(
            action_id="antiflood.set_action",
            description="Configurar acción de antiflood",
            schema=AntifloodSetActionParams,
            permissions=("admin", "moderator"),
            execute=_antiflood_set_action,
            requires_confirmation=False,
        )
    )
    registry.register(
        ActionDefinition(
            action_id="goodbye.toggle",
            description="Activar o desactivar mensaje de despedida",
            schema=GoodbyeToggleParams,
            permissions=("admin", "moderator"),
            execute=_goodbye_toggle,
            requires_confirmation=False,
        )
    )
    registry.register(
        ActionDefinition(
            action_id="goodbye.set_text",
            description="Actualizar texto de despedida",
            schema=GoodbyeSetTextParams,
            permissions=("admin", "moderator"),
            execute=_goodbye_set_text,
            requires_confirmation=False,
        )
    )
    registry.register(
        ActionDefinition(
            action_id="filter.add_word",
            description="Bloquear una palabra",
            schema=FilterAddWordParams,
            permissions=("admin", "moderator"),
            execute=_filter_add_word,
            requires_confirmation=False,
        )
    )
    registry.register(
        ActionDefinition(
            action_id="filter.remove_word",
            description="Desbloquear una palabra",
            schema=FilterRemoveWordParams,
            permissions=("admin", "moderator"),
            execute=_filter_remove_word,
            requires_confirmation=False,
        )
    )
