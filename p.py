from telethon import TelegramClient, events
from telethon.tl.functions.messages import CreateChatRequest, EditChatAboutRequest
import re
import asyncio
import os

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')

ABH = TelegramClient('userbot', api_id, api_hash)

# دالة إنشاء مجموعة جديدة
async def create_group(name, about):
    me = await ABH.get_me()
    result = await ABH(CreateChatRequest(
        users=[me.username],  # إضافة المستخدم لنفسه لإنشاء الكروب
        title=name
    ))
    group = result.chats[0]
    await ABH(EditChatAboutRequest(peer=group.id, about=about))
    return group.id, group.title

# دالة رئيسية لأمر /config
@ABH.on(events.NewMessage(pattern='/config'))
async def config_vars(event):
    me = await ABH.get_me()
    gidvar_value = None
    hidvar_value = None

    # الخطوة 1: البحث في الرسائل المحفوظة (الخاص)
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

    # الخطوة 2: إذا لم توجد الفارات، يتم إنشاء المجموعات
    newly_created = []
    if not gidvar_value:
        gidvar_value, gid_name = await create_group("مجموعة التخزين", "هذه المجموعة مخصصة لتخزين البيانات.")
        newly_created.append(("مجموعة التخزين", gidvar_value))

    if not hidvar_value:
        hidvar_value, hid_name = await create_group("مجموعة الإشعارات", "هذه المجموعة مخصصة للتنبيهات.")
        newly_created.append(("مجموعة الإشعارات", hidvar_value))

    # الخطوة 3: إذا تم الإنشاء، نحفظ الفارات برسالة في الخاص
    if newly_created:
        config_text = f'''#فارات السورس
لا تحذف الرسالة للحفاظ على كروبات السورس

مجموعة التخزين gidvar: {gidvar_value}
مجموعة الإشعارات hidvar: {hidvar_value}
        '''
        await ABH.send_message(me.id, config_text)

        # إرسال تقرير بالـ IDs إلى الخاص
        ids_text = "تم إنشاء الكروبات التالية:\n\n"
        for title, gid in newly_created:
            ids_text += f"**{title}**\nID: `{gid}`\n\n"
        await ABH.send_message(me.id, ids_text)

    # الخطوة 4: إرسال الرد النهائي لأمر /config
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
