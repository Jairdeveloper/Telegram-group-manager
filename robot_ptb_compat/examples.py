"""Ejemplos de uso de robot-ptb-compat."""

import os
from robot_ptb_compat.runtime import CompatApplicationBuilder
from robot_ptb_compat.transport import TelegramClient
from robot_ptb_compat.compat.handlers import CommandAdapter, MessageAdapter, CallbackAdapter
from robot_ptb_compat.compat.handlers import FiltersAdapter
from robot_ptb_compat.bridge import UpdateBridge, MessageBridge


async def example_basic_webhook():
    """Ejemplo básico de webhook."""
    app = (
        CompatApplicationBuilder(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        .build()
    )
    
    app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path="webhook",
        webhook_url=os.getenv("WEBHOOK_URL"),
    )


async def example_basic_polling():
    """Ejemplo básico de polling."""
    app = (
        CompatApplicationBuilder(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        .build()
    )
    
    app.run_polling()


async def example_with_handlers():
    """Ejemplo con handlers."""
    async def start_command(update, context):
        await update.message.reply_text("Hello!")
    
    async def help_command(update, context):
        await update.message.reply_text("Help text")
    
    async def echo_message(update, context):
        text = update.message.text
        await update.message.reply_text(f"You said: {text}")
    
    app = (
        CompatApplicationBuilder(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        .add_handler(CommandAdapter(commands=["start"], callback=start_command))
        .add_handler(CommandAdapter(commands=["help"], callback=help_command))
        .add_handler(MessageAdapter(
            callback=echo_message,
            filters=FiltersAdapter.text()
        ))
        .build()
    )
    
    app.run_polling()


async def example_with_callback():
    """Ejemplo con callback query."""
    async def start_command(update, context):
        keyboard = [
            [{"text": "Button 1", "callback_data": "btn1"}],
            [{"text": "Button 2", "callback_data": "btn2"}]
        ]
        await update.message.reply_text(
            "Choose:",
            reply_markup={"inline_keyboard": keyboard}
        )
    
    async def button_callback(update, context):
        data = update.callback_query.data
        await update.callback_query.message.reply_text(f"You pressed: {data}")
        await context.bot.answer_callback_query(update.callback_query.id)
    
    app = (
        CompatApplicationBuilder(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        .add_handler(CommandAdapter(commands=["start"], callback=start_command))
        .add_handler(CallbackAdapter(callback=button_callback))
        .build()
    )
    
    app.run_polling()


async def example_telegram_client():
    """Ejemplo de uso del TelegramClient."""
    client = TelegramClient(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    
    await client.send_message(
        chat_id=123456789,
        text="Hello from robot-ptb-compat!"
    )


async def example_bridge():
    """Ejemplo de uso de los bridges."""
    from telegram import Update
    
    # Supongamos que tenemos un Update de PTB
    # update = await bot.get_updates()
    
    # Convertir a formato interno
    # update_dict = UpdateBridge.to_internal(update)
    
    # Extraer información
    # chat_id = update_dict.get("message", {}).get("chat", {}).get("id")
    # user_id = update_dict.get("message", {}).get("from", {}).get("id")
    # text = update_dict.get("message", {}).get("text")
    
    pass


if __name__ == "__main__":
    import asyncio
    
    asyncio.run(example_basic_polling())
