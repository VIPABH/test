from telethon.tl.functions.channels import LeaveChannelRequest
from telethon import types, events
from Resources import *
from ABH import ABH
from telethon.tl.functions.messages import GetFullChatRequest, GetFullChannelRequest

@ABH.on(events.NewMessage(pattern=r"^رابط(?: المجموعة)?$"))
async def get_current_group_link(event):
    """استرجاع رابط الدعوة الافتراضي للمجموعة الحالية فقط"""
    chat_id = event.chat_id

    # التأكد أن المجموعة ضمن المجموعات المخزّنة
    if chat_id not in alert_ids:
        await event.reply("⚠️ هذه المجموعة غير موجودة ضمن المجموعات المخزّنة.")
        return

    # التأكد إنها مجموعة فعلاً
    if not str(chat_id).startswith("-100"):
        await event.reply("❌ هذا الأمر يُستخدم فقط داخل المجموعات.")
        return

    try:
        chat = await ABH.get_entity(chat_id)
        # تحديد نوع المجموعة (عادية أو سوبر)
        if getattr(chat, 'megagroup', False) or getattr(chat, 'broadcast', False):
            full = await ABH(GetFullChannelRequest(chat_id))
        else:
            full = await ABH(GetFullChatRequest(chat_id))

        # استرجاع الرابط الموجود مسبقًا
        link = getattr(full.full_chat, "exported_invite", None)
        if link and getattr(link, "link", None):
            await event.reply(
                f"🔗 **رابط المجموعة:**\n[{chat.title}]({link.link})",
                link_preview=False
            )
        else:
            await event.reply("🚫 لا يوجد رابط دعوة مفعّل لهذه المجموعة.")

    except Exception as e:
        print(f"❌ خطأ أثناء استرجاع الرابط للمجموعة {chat_id}: {e}")
        await event.reply("⚠️ حدث خطأ أثناء محاولة استرجاع الرابط.")
