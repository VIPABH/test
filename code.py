from ABH import ABH as client
from telethon import  events
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins


@client.on(events.NewMessage(pattern=r'\.admins'))
async def mention_admins_command(event):
    # التأكد من أن الأمر تم استخدامه داخل مجموعة وليست محادثة خاصة
    if not event.is_group:
        await event.reply("هذا الأمر مخصص للاستخدام داخل المجموعات فقط.")
        return

    chat = await event.get_chat()
    admins_list = []
    
    # جلب قائمة المشرفين في المجموعة
    async for user in client.iter_participants(chat, filter=ChannelParticipantsAdmins):
        # تخطي البوتات أو الحسابات المحذوفة
        if user.bot or user.deleted:
            continue
            
        # إنشاء رابط المنشن المخفي باسم المشرف
        admin_link = f"[{user.first_name}](tg://user?id={user.id})"
        admins_list.append(admin_link)
        
    if not admins_list:
        await event.reply("لم يتم العثور على مشرفين في هذه المجموعة.")
        return

    # دمج المنشنات في رسالة واحدة
    mentions_text = " ".join(admins_list)
    final_message = f"🚨 **تنبيه للمشرفين:**\n\n{mentions_text}"
    
    # حذف رسالة الأمر التي كتبها المستخدم (اختياري، لتنظيف الدردشة)
    try:
        await event.delete()
    except Exception:
        pass
        
    # إرسال الرسالة النهائية التي تحتوي على جميع المنشنات
    await client.send_message(chat, final_message, parse_mode='md')

print("المساعد يعمل الآن... اكتب .admins في أي مجموعة لتجربته.")
