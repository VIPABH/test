from telethon.tl.functions.messages import CreateChatRequest, EditChatAboutRequest
from telethon import TelegramClient, events
import os
import re
import asyncio

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
ABH = TelegramClient('s', api_id, 
@ABH.on(events.NewMessage(pattern='/config'))
async def config_vars(event):
    me = await ABH.get_me()
    gidvar_value = None
    hidvar_value = None
    async for msg in ABH.iter_messages(me.id):
        if not msg.text:
            continue
        gid_match = re.search(r'gidvar:\s*(.+)', msg.text, re.IGNORECASE)
        hid_match = re.search(r'hidvar:\s*(.+)', msg.text, re.IGNORECASE)
        if gid_match and not gidvar_value:
            gidvar_value = gid_match.group(1).strip()
        if hid_match and not hidvar_value:
            hidvar_value = hid_match.group(1).strip()
        if gidvar_value and hidvar_value:
            break
    response = f'''#فارات السورس
لا تحذف الرسالة للحفاظ على كروبات السورس

مجموعة التخزين gidvar:
{gidvar_value or " لم يتم العثور على الفار"}

مجموعة الإشعارات hidvar:
{hidvar_value or " لم يتم العثور على الفار"}
    '''
    await event.reply(response)
else:

async def main():
    await ABH.start()
    print("البرنامج يعمل... اضغط Ctrl+C للإيقاف.")
    await ABH.run_until_disconnected()

asyncio.run(main())
