from telethon import TelegramClient, events
import redis
from ABH import ABH as client
from Resources import * 
# معرف المطور (أنت) للتحكم بالاختصارات
OWNER_ID = wfffp  # ضع أيديك هنا

# --- 1. الموزع الذكي (الميدل وير) ---
# هذا الجزء هو المسؤول عن تحويل "تق" إلى "تقييد" تلقائياً قبل وصولها للأوامر
@client.on(events.NewMessage(incoming=True))
async def alias_resolver(event):
    if not event.text or not event.text[0] in ['/', '.', '!']:
        return

    parts = event.text.split(maxsplit=1)
    prefix = parts[0][0]
    trigger = parts[0][1:]
    args = parts[1] if len(parts) > 1 else ""

    # جلب الاسم الحقيقي
    real_command_name = r.hget("bot_aliases", trigger)

    if real_command_name:
        # تنظيف الاسم الحقيقي من أي رموز زائدة لضمان بناء نص سليم
        clean_name = real_command_name.lstrip('/.! ')
        new_text = f"{prefix}{clean_name} {args}".strip()
        
        # تحديث الرسالة
        event.message.message = new_text
        event.message.text = new_text
        
        print(f"🔄 جاري محاولة تشغيل: {new_text}")

        # البحث اليدوي عن المعالج الصحيح وتشغيله
        for handler, event_type in client.list_event_handlers():
            if isinstance(event_type, events.NewMessage):
                # التحقق إذا كان الـ Pattern الخاص بالأمر يطابق النص الجديد
                if event_type.filter(event):
                    try:
                        await handler(event)
                        print(f"✅ تم تشغيل الأمر بنجاح")
                        raise events.StopPropagation
                    except events.StopPropagation:
                        raise
                    except Exception as e:
                        print(f"❌ خطأ أثناء تشغيل الأمر: {e}")
        
        # إذا وصل الكود هنا يعني الـ pattern لم يتطابق
        print(f"⚠️ لم يتم العثور على أمر يطابق {new_text}")
        raise events.StopPropagation
@client.on(events.NewMessage(pattern=r'/(ربط|unalias) (.*)'))
async def manage_aliases(event):
    if event.sender_id != OWNER_ID:
        return

    cmd_type = event.pattern_match.group(1)
    data = event.pattern_match.group(2).split()

    if cmd_type == "ربط":
        if len(data) < 2:
            return await event.reply("❌ الاستخدام: `/ربط تقييد تق`")
        
        original, short = data[0], data[1]
        r.hset("bot_aliases", short, original)
        await event.reply(f"✅ تم! الآن `{short}` سيقوم بتنفيذ `{original}`")

    elif cmd_type == "unalias":
        short = data[0]
        if r.hdel("bot_aliases", short):
            await event.reply(f"🗑 تم حذف الاختصار `{short}`")

# --- مثال لواحد من الـ 140 أمر لديك (لا يحتاج تعديل) ---
@client.on(events.NewMessage(pattern='/تقييد'))
async def ban_handler(event):
    # هذا الأمر سيعمل سواء كتب المستخدم /تقييد أو كتب الاختصار الذي ربطته
    await event.reply("بشري، تم تنفيذ أمر التقييد بنجاح! 🔥")

# تشغيل البوت
print("Anymous Bot is running...")
