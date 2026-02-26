import os
import asyncio
import importlib

# Ensure adapter import succeeds (module checks TELEGRAM_BOT_TOKEN on import)
os.environ.setdefault('TELEGRAM_BOT_TOKEN', 'test-token')

mod = importlib.import_module('telegram_adapter')

class FakeMessage:
    def __init__(self, text):
        self.text = text
        self.replies = []
    async def reply_text(self, txt):
        print('REPLY:', txt)
        self.replies.append(txt)

class FakeUpdate:
    def __init__(self, text):
        self.message = FakeMessage(text)

async def run():
    upd = FakeUpdate('hola desde adapter_test')
    await mod.handle_message(upd, None)

if __name__ == '__main__':
    asyncio.run(run())
