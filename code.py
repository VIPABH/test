from ABH import *
from telethon import Button


@ABH.on(events.NewMessage(pattern=r"^زر(?:\s+(.+))?$"))
async def handler(event):

    # if not event.is_group:
    #     return

    full_text = event.pattern_match.group(1)

    if not full_text:
        return await event.reply(
            "يرجى كتابة الأزرار بعد الأمر، بصيغة:\n"
            "`اسم الزر الرابط اللون الايموجي`\n\n"
            "مثال:\n"
            "`زر المطور https://t.me/k_4x1 ازرق 🌚`\n\n"
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

    reply_msg = await event.get_reply_message()

    buttons = []
    row = []

    # تحويل أسماء الألوان إلى قيم Button
    colors = {
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

    for item in items:
        try:
            parts = item.split()

            if len(parts) < 2:
                continue

            # البحث عن الرابط
            url_index = next(
                i for i, x in enumerate(parts)
                if x.startswith(("http://", "https://", "tg://"))
            )

            # اسم الزر
            label = " ".join(parts[:url_index])

            # الرابط
            url = parts[url_index]

            # اللون اختياري
            style = None

            if len(parts) > url_index + 1:
                color = parts[url_index + 1].lower()
                style = colors.get(color)

            # الايموجي اختياري
            icon = (
                parts[url_index + 2]
                if len(parts) > url_index + 2
                else None
            )

            row.append(
                Button.url(
                    label,
                    url,
                    style=style,
                    icon=icon
                )
            )

            # زرين في كل صف
            if len(row) == 2:
                buttons.append(row)
                row = []

        except StopIteration:
            await ABH.send_message(
                1910015590,
                f"لم يتم العثور على رابط في الزر:\n{item}"
            )

        except Exception as e:
            await ABH.send_message(
                1910015590,
                f"حدث خطأ في الأزرار: {e}"
            )

    if row:
        buttons.append(row)

    if not buttons:
        return await event.reply(
            "لم يتم العثور على أزرار صالحة."
        )

    if reply_msg.media:
        await ABH.send_file(
            event.chat_id,
            reply_msg.media,
            caption=reply_msg.message or "",
            buttons=buttons
        )

    elif reply_msg.text:
        await event.respond(
            reply_msg.text,
            buttons=buttons
        )

    else:
        await event.reply(
            "لا يمكن نسخ نوع هذه الرسالة."
        )
