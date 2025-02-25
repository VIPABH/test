from telethon import TelegramClient, events
import os, re
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN') 
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
is_on = False
@ABH.on(events.NewMessage(pattern="تفعيل"))
async def activate(event):
    global is_on
    await event.reply("تم التفعيل")
    is_on = True
@ABH.on(events.NewMessage(pattern="تعطيل"))
async def deactivate(event):
    global is_on
    await event.reply("تم التعطيل")
    is_on = False
@ABH.on(events.MessageEdited)
async def handler(event):
    if not is_on:
        return
    if event.message.media and isinstance(event.message.media, events.MessageMediaDocument) or event.message.text and re.search(r'http[s]?://', event.message.text):
        await event.reply('تم تعديل مرفق في هذه الرسالة!')        
ABH.run_until_disconnected()
