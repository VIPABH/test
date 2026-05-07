from telethon import TelegramClient, events
import redis
import asyncio
from ABH import ABH as client
from Resources import * 

# الاتصال بـ Redis (تأكد من وجود 'r' في ملف Resources)
# r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# معرف المطور (أنت)
# OWNER_ID = 123456789 # ضع أيديك هنا أو تأكد من تعريفه في Resources

# --- 1. الموزع الذكي (Alias Resolver & Event Injector) ---
@client.on(events.NewMessage(incoming=True))
async def alias_resolver(event):
    # دعم الرموز الأساسية لسورس Anymous
    if not event.text or not event.text[0] in ['/', '.', '!']:
        return

    # تحليل النص المستلم
    parts = event.text.split(maxsplit=1)
    prefix = parts[0][0]  
    trigger = parts[0][1:] # اسم الاختصار (مثلاً: ها)
    args = parts[1] if len(parts) > 1 else ""

    # جلب الأمر الحقيقي من قاعدة البيانات
    real_command_name = r.hget("bot_aliases", trigger)

    if real_command_name:
        # تنظيف اسم الكلمة الأصلية وبناء النص الجديد
        clean_name = real_command_name.lstrip('/.! ')
        new_text = f"{prefix}{clean_name} {args}".strip()
        
        # التقاط الـ Reply إذا كان المستخدم راد على شخص
        reply_msg = await event.get_reply_message()
        
        # تحديث كائن الرسالة داخلياً
        event.message.message = new_text
        event.message.text = new_text
        
        print(f"🔄 تحويل: {trigger} -> {new_text}")

        # البحث في كافة الـ 140 أمر عن المطابق
        for handler, event_type in client.list_event_handlers():
            if isinstance(event_type, events.NewMessage):
                # فحص الـ Pattern والـ Filters للأمر الأصلي
                if event_type.filter(event):
                    try:
                        # حقن الـ Reply يدوياً لضمان عمل دوال التقييد والطرد
                        if reply_msg:
                            event._reply_message = reply_msg
                            event.message.reply_to_msg_id = reply_msg.id
                        
                        # تشغيل الدالة الأصلية للأمر
                        await handler(event)
                        print(f"✅ تم تنفيذ الأمر بنجاح في الشات")
                        
                        # إيقاف التكرار
                        raise events.StopPropagation
                    except events.StopPropagation:
                        raise
                    except Exception as e:
                        print(f"❌ خطأ برمي داخل الدالة: {e}")
        
        # إذا لم يجد تطابق بعد التحويل
        print(f"⚠️ تحويل ناجح ولكن لم يتم العثور على Handler لـ: {new_text}")
        raise events.StopPropagation

# --- 2. أوامر التحكم بالاختصارات (للمطور فقط) ---
@client.on(events.NewMessage(pattern=r'^/(ربط|حذف_ربط) (.*)'))
async def manage_aliases(event):
    if event.sender_id != OWNER_ID:
        return

    cmd_type = event.pattern_match.group(1)
    data = event.pattern_match.group(2).split()

    if cmd_type == "ربط":
        if len(data) < 2:
            return await event.reply("⚠️ الاستخدام: `/ربط تقييد ها`")
        
        original = data[0].replace('/', '')
        short = data[1].replace('/', '')
        
        r.hset("bot_aliases", short, original)
        await event.reply(f"🚀 **تم الربط بنجاح**\n\nالأصل: `{original}`\nالاختصار: `{short}`\n\nجرب الآن إرسال `{short}` بالرد على مستخدم.")

    elif cmd_type == "حذف_ربط":
        short = data[0].replace('/', '')
        if r.hdel("bot_aliases", short):
            await event.reply(f"🗑 تم حذف الاختصار `{short}`.")
        else:
            await event.reply(f"❌ الاختصار غير موجود.")

# --- قسم الأوامر الـ 140 (تبقى كما هي) ---
# مثال للتجربة:
# @client.on(events.NewMessage(pattern='/تقييد'))
# async def ban_handler(event):
#     if event.is_reply:
#         reply = await event.get_reply_message()
#         await event.reply(f"تم تقييد {reply.sender_id} بنجاح")

print("Anymous Bot is running with Dynamic Aliases...")
