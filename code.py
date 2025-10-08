import json
import os
import re
from telethon import events
from ABH import ABH  # استيراد الكيان

def fix_common_json_errors(text: str) -> str:
    text = text.strip()
    text = re.sub(r',\s*([\]}])', r'\1', text)
    if text.count('"') % 2 != 0:
        text += '"'
    if text.startswith('[') and not text.endswith(']'):
        text += ']'
    elif text.startswith('{') and not text.endswith('}'):
        text += '}'
    return text

@ABH.on(events.NewMessage(pattern=r'^تنظيف$'))
async def clean_json_handler(event):
    if not event.is_reply:
        await event.reply("❌ يرجى الرد على ملف JSON.")
        return

    reply_msg = await event.get_reply_message()
    if not reply_msg.media:
        await event.reply("❌ الملف غير موجود.")
        return

    file_path = await reply_msg.download_media()
    original_name = os.path.basename(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        original_text = f.read()

    # أول محاولة - بدون تعديل
    try:
        json.loads(original_text)
    except json.JSONDecodeError as e:
        error_msg = (
            f"❌ فشل في قراءة JSON.\n"
            f"📌 **السطر:** {e.lineno}\n"
            f"📍 **العمود:** {e.colno}\n"
            f"💬 **الرسالة:** {e.msg}"
        )
        await event.reply(error_msg)

        # محاولة إصلاح الأخطاء السطحية
        fixed_text = fix_common_json_errors(original_text)
        try:
            json.loads(fixed_text)
        except json.JSONDecodeError as e2:
            error_msg2 = (
                f"❌ لم يتمكن البوت من إصلاح الخطأ تلقائيًا.\n"
                f"📌 **السطر:** {e2.lineno}\n"
                f"📍 **العمود:** {e2.colno}\n"
                f"💬 **الرسالة:** {e2.msg}\n\n"
                f"⚠️ من الأفضل فتح الملف يدويًا عند هذا السطر وإصلاح المشكلة."
            )
            await event.reply(error_msg2)
            os.remove(file_path)
            return
        else:
            # حفظ الملف المصحح بعد نجاح الإصلاح
            with open(original_name, "w", encoding="utf-8") as f:
                f.write(fixed_text)
            await event.reply(file=original_name, message="✅ تم إصلاح الملف بعد تعديل تلقائي.")
            os.remove(file_path)
            os.remove(original_name)
            return
    else:
        await event.reply("✅ الملف سليم ولا يحتوي على أخطاء.")
        os.remove(file_path)
