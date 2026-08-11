from ABH import *
from telethon import Button
from urllib.parse import urlparse


COLORS = {
    "ازرق": "primary",
    "أزرق": "primary",
    "blue": "primary",

    "احمر": "danger",
    "أحمر": "danger",
    "red": "danger",

    "اخضر": "success",
    "أخضر": "success",
    "green": "success",
}


def valid_url(url):
    try:
        if url.startswith("tg://"):
            return True

        parsed = urlparse(url)

        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.netloc)
        )

    except Exception:
        return False


@ABH.on(events.NewMessage(pattern=r"^زر(?:\s+(.+))?$"))
async def handler(event):

    # if not event.is_group:
    #     return

    full_text = event.pattern_match.group(1)

    if not full_text:
        return await event.reply(
            "يرجى كتابة الأزرار بعد الأمر، بصيغة:\n\n"
            "`زر [اللون] [اسم الزر] الرابط [الايموجي]`\n\n"
            "مثال:\n"
            "`زر ازرق المطور https://t.me/k_4x1 🌚`\n\n"
            "اللون والايموجي اختياريان.\n"
            "لإضافة زر جديد استخدم `|`"
        )

    if not event.is_reply:
        return await event.reply(
            "يجب الرد على الرسالة التي تريد نسخها."
        )

    items = [
        item.strip()
        for item in full_text.split("|")
        if item.strip()
    ]

    if len(items) > 20:
        return await event.reply(
            "الحد الأقصى هو 20 زرًا."
        )

    reply_msg = await event.get_reply_message()

    buttons = []
    row = []
    invalid = []

    for item in items:

        parts = item.split()

        if not parts:
            invalid.append(item)
            continue

        # البحث عن الرابط
        url_index = None

        for i, value in enumerate(parts):
            if value.startswith(("http://", "https://", "tg://")):
                url_index = i
                break

        if url_index is None:
            invalid.append(item)
            continue

        url = parts[url_index]

        # التحقق من الرابط
        if not valid_url(url):
            invalid.append(item)
            continue

        # ------------------------------------------------
        # كل شيء قبل الرابط
        # ------------------------------------------------

        before_url = parts[:url_index]

        style = None
        label_parts = []

        # إذا أول كلمة لون
        if before_url:
            first = before_url[0].lower()

            if first in COLORS:
                style = COLORS[first]
                label_parts = before_url[1:]
            else:
                label_parts = before_url

        # اسم الزر
        label = " ".join(label_parts).strip()

        # اسم افتراضي إذا لم يكتب اسم
        if not label:
            label = "اضغط هنا"

        if len(label) > 64:
            invalid.append(item)
            continue

        # ------------------------------------------------
        # ما بعد الرابط = الايقونة
        # ------------------------------------------------

        after_url = parts[url_index + 1:]

        icon = None

        if len(after_url) > 1:
            # أكثر من شيء بعد الرابط
            invalid.append(item)
            continue

        if after_url:
            icon = after_url[0]

            if len(icon) > 10:
                invalid.append(item)
                continue

        # ------------------------------------------------
        # إنشاء الزر
        # ------------------------------------------------

        try:

            button = Button.url(
                label,
                url,
                style=style,
                icon=icon
            )

            row.append(button)

            # زرين في كل صف
            if len(row) == 2:
                buttons.append(row)
                row = []

        except Exception:
            invalid.append(item)

    # إضافة الصف الأخير
    if row:
        buttons.append(row)

    # لا توجد أزرار
    if not buttons:
        return await event.reply(
            "لم يتم العثور على أي أزرار صالحة."
        )

    # رسالة تحذير للأزرار الخاطئة
    warning = ""

    if invalid:

        invalid_text = "\n".join(
            f"• `{x}`"
            for x in invalid[:5]
        )

        warning = (
            "\n\n⚠️ تم تجاهل بعض الأزرار:\n"
            f"{invalid_text}"
        )

        if len(invalid) > 5:
            warning += (
                f"\n... و {len(invalid) - 5} أخرى."
            )

    try:

        # رسالة تحتوي على ميديا
        if reply_msg.media:

            await ABH.send_file(
                event.chat_id,
                reply_msg.media,
                caption=reply_msg.message or "",
                buttons=buttons
            )

        # رسالة نصية
        elif reply_msg.message:

            await ABH.send_message(
                event.chat_id,
                reply_msg.message,
                buttons=buttons
            )

        else:

            return await event.reply(
                "لا يمكن نسخ نوع هذه الرسالة."
            )

        # حذف أمر زر
        try:
            await event.delete()
        except Exception:
            pass

        # إرسال التحذير إذا كان هناك زر خاطئ
        if warning:
            await ABH.send_message(
                event.chat_id,
                f"تم إنشاء الأزرار بنجاح.{warning}"
            )

    except Exception:

        return await event.reply(
            "حدث خطأ أثناء إنشاء الرسالة والأزرار."
        )
