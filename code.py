from ABH import ABH as client
from telethon import events
import asyncio
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
            
        # إنشاء منشن مخفي لكل مشرف (النقطة أو الفراغ يحمل رابط الـ ID)
        # يمكنك تغيير الحرف (.) بأي رمز تريده أو مسافة مخفية
        admin_link = f"[\u200b](tg://user?id={user.id})"
        admins_list.append(admin_link)
        
    if not admins_list:
        await event.reply("لم يتم العثور على مشرفين في هذه المجموعة.")
        return

    # دمج المنشنات المخفية مع نص عادي تختاره (مثلاً: تنبيه إداري)
    mentions_text = "".join(admins_list)
    
    # الرسالة التي ستظهر للمستخدمين بشكل طبيعي مضاف إليها المنشنات المخفية (Zero-width)
    final_message = f"🚨 **تنبيه: تم استدعاء المشرفين.**{mentions_text}"
    
    # حذف رسالة الأمر التي كتبها المستخدم لتنظيف الدردشة
    try:
        await event.delete()
    except Exception:
        pass
        
    # إرسال الرسالة النهائية
    await client.send_message(chat, final_message, parse_mode='md')

print("المساعد يعمل الآن... اكتب .admins في أي مجموعة لتجربته.")
