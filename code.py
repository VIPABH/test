from telethon.tl.types import InputDocument
from Resources import mention, hint, wfffp
# from other import botuse, is_assistant
from telethon import Button, events
# from Program import chs
import random, redis
from ABH import ABH
async def chs(e, t):
    ABH.send_message(e.chat_id, t, reply_to=e.id)
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
session = {}
banned = ['وضع ردي', 'وضع رد', 'وضع رد مميز', 'الغاء', 'حذف رد', 'حذف الردود', 'عرض الردود', 'حذف ردي']
@ABH.on(events.NewMessage)
async def s(e):
    if e.media:
        await e.reply('??')
