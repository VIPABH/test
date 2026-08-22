from Resources import *
from ABH import *
import uuid, re
@ABH.on(events.NewMessage(incoming=True, pattern="/test_copy"))
async def test_server_side_copy(event):
    # اطلب من المستخدم يرد على رسالة فيها ميديا (صورة/فيديو/صوت) بهذا الأمر
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.reply("رد على رسالة فيها ميديا وسوي /test_copy")
        return

    try:
        # هذا يسوي نسخ server-side بدون تحميل محلي
        # 'me' = محادثة "Saved Messages" تبع حساب البوت نفسه
        copied_msg = await ABH.send_file(
            'me',
            file=reply.media,
            caption=f"نسخة اختبار - من {event.sender_id}"
        )
        await event.reply(
            f"تم النسخ بنجاح ✅\n"
            f"chat_id الجديد: {copied_msg.peer_id}\n"
            f"message_id الجديد: {copied_msg.id}"
        )
    except Exception as e:
        await event.reply(f"فشل النسخ ❌\n{type(e).__name__}: {e}")
