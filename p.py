from telethon import TelegramClient, events
import asyncio, os

api_id = int(os.getenv('API_ID_6'))
api_hash = os.getenv('API_HASH_6')
print(api_id)
ABH = TelegramClient('session_6', api_id, api_hash)
@ABH.on(events.NewMessage)
async def group_save(event):
    uid = event.sender_id
    sender = await event.get_sender()
    print(sender)
    print(sender.bot)
def main():
    ABH.start()  # ستطلب الجلسة إدخال الرقم أول مرة فقط
    print("UserBot is running...")
    ABH.run_until_disconnected()

if __name__ == '__main__':
    main()
