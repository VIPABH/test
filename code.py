from telethon import events, Button
from Resources import *
from ABH import ABH
import uuid
async def saveNum(e, uid):
    id = e.sender_id
    if not uid.startswith(str(id)):
        await e.reply("عذراً عزيزي لا يمكنك تعيين رقم")
        return
    num = e.text
    if not num.isdigit():
        await e.reply("عزيزي حاول ترسل الرقم بدون اي كلام")
        return
    NUM = e.text
@ABH.on(events.NewMessage(pattern="^تعيين رقم$"))
async def setNUM(e):
    id = str(uuid.uuid4())[:6]
    b = Button.url("اضغط لتعيين الرقم", url=f"https://t.me/{(await ABH.get_me()).username}?start={id}")
    await e.reply("تم فتح جلسة لتعيين الرقم")
@ABH.on(events.NewMessage)
def sdd(e):
    if e.text == NUM:
        await e.reply("تم حزرت الرقم")
    else:
        return
