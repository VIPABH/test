import json
import os
import re
from telethon import events
from ABH import ABH  # ← استيراد الكيان مباشرة باسم ABH

def fix_common_json_errors(text: str) -> str:
    """
    إصلاح الأخطاء الشائعة في ملفات JSON الكبيرة:
    - إزالة الفواصل الزائدة
    - إغلاق علامات الاقتباس
    - إغلاق الأقواس الناقصة
    """
    text = text.strip()

    # إزالة الفواصل الزائدة في نهاية القوائم أو القواميس
    text = re.sub(r',\s*([\]}])', r'\1', text)

    # إغلاق علامات الاقتباس إذا كانت غير متوازنة
    if text.count('"') % 2 != 0:
        text += '"'

    # إغلاق القوس أو القوس المربع الناقص
    if text.startswith('[') and not text.endswith(']'):
        text += ']'
    elif text.startswith('{') and not text.endswith('}'):
        text += '}'

    return text

@ABH.on(events.NewMessage(pattern=r'^تنظيف$'))
async def clean_json_handler(event):
    if not event.is_reply:
        await event.reply("❌ يرجى الرد على ملف JSON المراد تنظيفه.")
        return

    reply_msg = await event.get_reply_message()

    if not reply_msg.media:
        await event.reply("❌ الرسالة المردود عليها لا تحتوي على ملف.")
        return

    # تنزيل الملف بنفس اسمه الأصلي
    file_path = await reply_msg.download_media()
    original_name = os.path.basename(file_path)

    # قراءة النص الأصلي للملف
    with open(file_path, "r", encoding="utf-8") as f:
        original_text = f.read()

    fixed_text = original_text
    error_fixed = False

    # محاولة التحميل العادي
    try:
        json.loads(original_text)
    except json.JSONDecodeError:
        # إصلاح الأخطاء الشائعة
        fixed_text = fix_common_json_errors(original_text)
        try:
            json.loads(fixed_text)
            error_fixed = True
        except json.JSONDecodeError:
            await event.reply("❌ لم يتمكن البوت من إصلاح الملف. الخطأ كبير أو غير قياسي.")
            os.remove(file_path)
            return

    # حفظ الملف المصحح بنفس الاسم الأصلي
    with open(original_name, "w", encoding="utf-8") as f:
        f.write(fixed_text)

    # إرسال الملف إليك بنفس الاسم
    caption = "✅ تم تنظيف الملف بنجاح."
    if error_fixed:
        caption += "\n🧰 تم إصلاح بعض الأخطاء البسيطة (مثل اقتباس أو قوس ناقص)."

    await event.reply(file=original_name, message=caption)

    # حذف الملفات المؤقتة بعد الإرسال
    os.remove(file_path)
    os.remove(original_name)

# تشغيل الكيان
ABH.start()
ABH.run_until_disconnected()
