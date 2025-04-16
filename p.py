from telethon import TelegramClient, events
import os, asyncio

api_id = int(os.getenv('API_ID', '123456'))
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')

ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.NewMessage)
async def e(event):
    message_text = '>>>>'
    msg = await ABH.send_file(event.chat_id, file='https://files.catbox.moe/k44qq6.mp4', caption=message_text)
    await asyncio.sleep(1)
    await msg.delete_media()
    await ABH.send_message(event.chat_id, "تم حذف الفيديو!")

ABH.run_until_disconnected()
