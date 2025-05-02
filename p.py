from telethon import TelegramClient, events
import yt_dlp
import os
import re
import asyncio

# قراءة المتغيرات من البيئة
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')

# إنشاء الكلاينت
ABH = TelegramClient('s', api_id, api_hash)

@ABH.on(events.NewMessage(pattern='/config'))
async def config_vars(event):
    me = await ABH.get_me()
    gidvar_value = None
    hidvar_value = None

    # تصفح الرسائل المحفوظة
    async for msg in ABH.iter_messages(me.id):
        if not msg.text:
            continue

        # استخدام regex لاستخراج القيم
        gid_match = re.search(r'gidvar:\s*(.+)', msg.text, re.IGNORECASE)
        hid_match = re.search(r'hidvar:\s*(.+)', msg.text, re.IGNORECASE)

        if gid_match and not gidvar_value:
            gidvar_value = gid_match.group(1).strip()

        if hid_match and not hidvar_value:
            hidvar_value = hid_match.group(1).strip()

        # نخرج من اللوب عند العثور على القيمتين
        if gidvar_value and hidvar_value:
            break

    # الرد بالتقرير
    response = f'''#فارات السورس
لا تحذف الرسالة للحفاظ على كروبات السورس

مجموعة التخزين gidvar:
{gidvar_value or "❌ لم يتم العثور على القيمة"}

مجموعة الإشعارات hidvar:
{hidvar_value or "❌ لم يتم العثور على القيمة"}
    '''
    await event.reply(response)

async def main():
    await ABH.start()
    print("البرنامج يعمل... اضغط Ctrl+C للإيقاف.")
    await ABH.run_until_disconnected()

asyncio.run(main())
