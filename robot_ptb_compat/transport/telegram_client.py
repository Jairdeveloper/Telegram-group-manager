"""Telegram Client wrapper para PTB."""

from typing import Any, Dict, List, Optional, Union

try:
    from telegram import Bot as PTBBot
    from telegram import Chat, ChatMember, Message, Update, User as PTBUser
    from telegram.error import TelegramError
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False
    PTBBot = None
    TelegramError = Exception


class TelegramClient:
    """Cliente Telegram que envuelve PTB Bot."""

    def __init__(
        self,
        token: str,
        bot: Optional[Any] = None,
    ):
        """Inicializa el cliente.

        Args:
            token: Token del bot
            bot: Instancia de Bot (opcional)
        """
        self._token = token
        self._bot = bot

        if not self._bot and HAS_TELEGRAM and token:
            self._bot = PTBBot(token=token)

    @property
    def bot(self) -> Optional[Any]:
        """Obtiene el bot de PTB."""
        return self._bot

    @property
    def token(self) -> str:
        """Obtiene el token."""
        return self._token

    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: Optional[str] = None,
        entities: Optional[List[Any]] = None,
        disable_web_page_preview: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[Any] = None,
        **kwargs
    ) -> Any:
        """Envía un mensaje.

        Args:
            chat_id: ID del chat
            text: Texto del mensaje
            parse_mode: Modo de parseo
            entities: Entidades
            disable_web_page_preview: Desactivar previsualización
            disable_notification: Desactivar notificación
            reply_to_message_id: ID del mensaje a responder
            allow_sending_without_reply: Permitir enviar sin respuesta
            reply_markup: Markup del teclado

        Returns:
            Mensaje enviado
        """
        if not self._bot:
            return None

        return await self._bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=reply_markup,
            **kwargs
        )

    async def edit_message_text(
        self,
        text: str,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        parse_mode: Optional[str] = None,
        entities: Optional[List[Any]] = None,
        disable_web_page_preview: Optional[bool] = None,
        reply_markup: Optional[Any] = None,
        **kwargs
    ) -> Any:
        """Edita un mensaje.

        Args:
            text: Nuevo texto
            chat_id: ID del chat
            message_id: ID del mensaje
            inline_message_id: ID del mensaje inline
            parse_mode: Modo de parseo
            entities: Entidades
            disable_web_page_preview: Desactivar previsualización
            reply_markup: Markup del teclado

        Returns:
            Mensaje editado
        """
        if not self._bot:
            return None

        return await self._bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
            parse_mode=parse_mode,
            entities=entities,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup,
            **kwargs
        )

    async def delete_message(
        self,
        chat_id: Union[int, str],
        message_id: int,
        **kwargs
    ) -> bool:
        """Elimina un mensaje.

        Args:
            chat_id: ID del chat
            message_id: ID del mensaje

        Returns:
            True si se eliminó
        """
        if not self._bot:
            return False

        return await self._bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
            **kwargs
        )

    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None,
        url: Optional[str] = None,
        cache_time: Optional[int] = None,
        **kwargs
    ) -> bool:
        """Responde a un callback query.

        Args:
            callback_query_id: ID del callback query
            text: Texto de la respuesta
            show_alert: Mostrar alerta
            url: URL
            cache_time: Tiempo de cache

        Returns:
            True si se respondió
        """
        if not self._bot:
            return False

        return await self._bot.answer_callback_query(
            callback_query_id=callback_query_id,
            text=text,
            show_alert=show_alert,
            url=url,
            cache_time=cache_time,
            **kwargs
        )

    async def get_me(self) -> Optional[Any]:
        """Obtiene información del bot.

        Returns:
            Información del bot
        """
        if not self._bot:
            return None

        return await self._bot.get_me()

    async def get_chat(self, chat_id: Union[int, str]) -> Optional[Any]:
        """Obtiene información del chat.

        Args:
            chat_id: ID del chat

        Returns:
            Información del chat
        """
        if not self._bot:
            return None

        return await self._bot.get_chat(chat_id=chat_id)

    async def get_chat_member(
        self,
        chat_id: Union[int, str],
        user_id: int,
    ) -> Optional[Any]:
        """Obtiene un miembro del chat.

        Args:
            chat_id: ID del chat
            user_id: ID del usuario

        Returns:
            Información del miembro
        """
        if not self._bot:
            return None

        return await self._bot.get_chat_member(
            chat_id=chat_id,
            user_id=user_id
        )

    async def set_webhook(
        self,
        url: str,
        certificate: Optional[Any] = None,
        max_connections: int = 40,
        allowed_updates: Optional[List[str]] = None,
        drop_pending_updates: bool = False,
        secret_token: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Configura el webhook.

        Args:
            url: URL del webhook
            certificate: Certificado
            max_connections: Conexiones máximas
            allowed_updates: Updates permitidos
            drop_pending_updates: Descartar updates pendientes
            secret_token: Token secreto

        Returns:
            True si se configuró
        """
        if not self._bot:
            return False

        return await self._bot.set_webhook(
            url=url,
            certificate=certificate,
            max_connections=max_connections,
            allowed_updates=allowed_updates,
            drop_pending_updates=drop_pending_updates,
            secret_token=secret_token,
            **kwargs
        )

    async def delete_webhook(
        self,
        drop_pending_updates: bool = False,
    ) -> bool:
        """Elimina el webhook.

        Args:
            drop_pending_updates: Descartar updates pendientes

        Returns:
            True si se eliminó
        """
        if not self._bot:
            return False

        return await self._bot.delete_webhook(
            drop_pending_updates=drop_pending_updates
        )

    async def get_webhook_info(self) -> Dict[str, Any]:
        """Obtiene información del webhook.

        Returns:
            Información del webhook
        """
        if not self._bot:
            return {}

        return await self._bot.get_webhook_info()

    async def get_updates(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        timeout: Optional[int] = None,
        allowed_updates: Optional[List[str]] = None,
    ) -> List[Any]:
        """Obtiene updates.

        Args:
            offset: Offset
            limit: Límite
            timeout: Timeout
            allowed_updates: Updates permitidos

        Returns:
            Lista de updates
        """
        if not self._bot:
            return []

        return await self._bot.get_updates(
            offset=offset,
            limit=limit,
            timeout=timeout,
            allowed_updates=allowed_updates,
        )


__all__ = ["TelegramClient"]
