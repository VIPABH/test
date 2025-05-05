from telethon import TelegramClient, events
import asyncio, os

api_id = int(os.getenv('API_ID_6'))
api_hash = os.getenv('API_HASH_6')
print(api_id)
ABH = TelegramClient('session_6', api_id, api_hash)

@ABH.on(events.NewMessage(outgoing=True))
async def handle_outgoing(event):
    await event.reply('Hello, this is a test message!')

@ABH.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def handle_private(event):
    await event.reply('Hello!')

def main():
    ABH.start()  # ستطلب الجلسة إدخال الرقم أول مرة فقط
    print("UserBot is running...")
    ABH.run_until_disconnected()

if __name__ == '__main__':
    main()
