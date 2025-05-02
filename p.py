from telethon import TelegramClient, events
from telethon.tl.functions.channels import CreateChannelRequest
import re
import asyncio
import os

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')

ABH = TelegramClient('s', api_id, api_hash)

# دالة إنشاء سوبر كروب جديد
async def create_group(name, about):
    result = await ABH(CreateChannelRequest(
        title=name,
        about=about,
        megagroup=True  # لإنشاء سوبر كروب
    ))
    group = result.chats[0]
    return group.id, group.title

# أمر /config
@ABH.on(events.NewMessage(pattern='/config'))
async def config_vars(event):
    me = await ABH.get_me()
    gidvar_value = None
    hidvar_value = None

    # الخطوة 1: البحث في الرسائل المحفوظة
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

    # الخطوة 2: إنشاء المجموعات إذا لم تكن موجودة
    newly_created = []
    if not gidvar_value:
        gidvar_value, gid_name = await create_group("مجموعة التخزين", "هذه المجموعة مخصصة لتخزين البيانات.")
        newly_created.append(("مجموعة التخزين", gidvar_value))

    if not hidvar_value:
        hidvar_value, hid_name = await create_group("مجموعة الإشعارات", "هذه المجموعة مخصصة للتنبيهات.")
        newly_created.append(("مجموعة الإشعارات", hidvar_value))

    # الخطوة 3: حفظ الفارات الجديدة في الرسائل المحفوظة
    if newly_created:
        config_text = f'''#فارات السورس
لا تحذف الرسالة للحفاظ على كروبات السورس

مجموعة التخزين gidvar: {gidvar_value}
مجموعة الإشعارات hidvar: {hidvar_value}
        '''
        await ABH.send_message(me.id, config_text)

        # إرسال تقرير خاص
        ids_text = "تم إنشاء الكروبات التالية:\n\n"
        for title, gid in newly_created:
            ids_text += f"**{title}**\nID: `{gid}`\n\n"
        await ABH.send_message(me.id, ids_text)

    # الخطوة 4: الرد على أمر /config
    response = f'''#فارات السورس
لا تحذف الرسالة للحفاظ على كروبات السورس

مجموعة التخزين gidvar:
{gidvar_value or "❌ لم يتم العثور على الفار"}

مجموعة الإشعارات hidvar:
{hidvar_value or "❌ لم يتم العثور على الفار"}
    '''
    await event.reply(response)

# تشغيل الكلاينت
async def main():
    await ABH.start()
    print("البرنامج يعمل... اضغط Ctrl+C للإيقاف.")
    await ABH.run_until_disconnected()

asyncio.run(main())
