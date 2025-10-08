import os
from telethon import events
from ABH import ABH
from json_repair import repair_json

@ABH.on(events.NewMessage(pattern=r'^تنظيف$'))
async def clean_json_handler(event):
    if not event.is_reply:
        await event.reply("❌ يرجى الرد على ملف JSON المراد تنظيفه.")
        return

    reply_msg = await event.get_reply_message()

    if not reply_msg.media:
        await event.reply("❌ هذه الرسالة لا تحتوي على ملف.")
        return

    # تحميل الملف مؤقتًا
    file_path = await reply_msg.download_media()
    original_name = os.path.basename(file_path)

    try:
        # قراءة النص الأصلي
        with open(file_path, "r", encoding="utf-8") as f:
            original_text = f.read()

        # إصلاح الأخطاء تلقائيًا باستخدام json-repair
        fixed_text = repair_json(original_text)

        # حفظ الملف المصحح بنفس الاسم الأصلي
        with open(original_name, "w", encoding="utf-8") as f:
            f.write(fixed_text)

        # إرسال الملف المصحح للمستخدم
        caption = (
            "✅ تم إصلاح ملف JSON بنجاح.\n"
            "🧰 تم استخدام json-repair لمعالجة الأخطاء المعقدة."
        )
        await event.reply(file=original_name, message=caption)

    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء معالجة الملف:\n`{str(e)}`")

    finally:
        # تنظيف الملفات المؤقتة
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(original_name):
            os.remove(original_name)

# تشغيل الكيان
ABH.start()
ABH.run_until_disconnected()
