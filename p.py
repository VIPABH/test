from telethon import TelegramClient, events
import yt_dlp
import os

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
ABH = TelegramClient('code', api_id, api_hash)


import re

@ABH.on(events.NewMessage(pattern='/config'))
async def config_vars(event):
    me = await ABH.get_me()
    gidvar_value = None
    hidvar_value = None

    async for msg in ABH.iter_messages(me.id):
        if not msg.text:
            continue

        # نستخدم regex لاستخراج القيم بعد gidvar: و hidvar:
        gid_match = re.search(r'gidvar:\s*(.+)', msg.text, re.IGNORECASE)
        hid_match = re.search(r'hidvar:\s*(.+)', msg.text, re.IGNORECASE)

        if gid_match:
            gidvar_value = gid_match.group(1).strip()

        if hid_match:
            hidvar_value = hid_match.group(1).strip()

        # إذا وجدنا القيمتين، لا داعي لإكمال البحث
        if gidvar_value and hidvar_value:
            break

    response = f'''#فارات السورس
لا تحذف الرسالة للحفاظ على كروبات السورس

مجموعة التخزين gidvar:
{gidvar_value or "❌ لم يتم العثور على القيمة"}

مجموعة الإشعارات hidvar:
{hidvar_value or "❌ لم يتم العثور على القيمة"}
    '''
    await event.reply(response)
ABH.run_until_disconnected()
