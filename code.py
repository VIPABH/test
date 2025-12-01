from telethon import TelegramClient, events, Button
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import asyncio, smtplib, os
default_smtp_server = "smtp.gmail.com"
default_smtp_port = 465
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
user_states = {}
ABH = TelegramClient('session_name', api_id, api_hash)
async def setemil(e):
    t = e.text
    await e.reply(str(t))
@ABH.on(events.NewMessage)
async def start(e):
    t = e.text
    if t == '/start':
        b = [Button.inline('تعيين كلايش', data='set')]
        await e.reply('اهلا اخي , عندك طاقة تشد؟', button=b)
    elif t in ('تعيين الكلايش',  'تعيين كلايش', '/start'):
        b = [Button.inline('تعيين البريد والباسورد', data='setemil'), Button.inline('تعيين الرسالة', data='setmessage')]
        await e.reply('اختار من الازرار حته نبدي', button=b)
@ABH.on(events.callbackquery)
async def callstart(e):
    data = e.data.decode('utf-8')
    if data == 'setemil':
        await e.reply('ارسل الايميل')
        await setemil(e)
    # elif data == 'setmessage':
        # await e.reply('ارسل الايميل')
ABH.start(bot_token=bot_token)
ABH.run_until_disconnected()
