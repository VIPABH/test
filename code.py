from ABH import *

@ABH.on(events.NewMessage(pattern=r"^زر(?:\s+(.+))?$"))
async def handler(event):

    if not event.is_group:
        return

    full_text = event.pattern_match.group(1)

    if not full_text:
        return await event.reply(
            "يرجى كتابة الأزرار بعد الأمر، بصيغة:\n"
            "`اسم الزر الرابط اللون الايموجي`\n\n"
            "مثال:\n"
            "`زر المطور https://t.me/k_4x1 blue 🌚`\n\n"
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

    for item in items:
        try:
            parts = item.split()

            if len(parts) < 2:
                continue

            # الرابط
            url_index = next(
                i for i, x in enumerate(parts)
                if x.startswith(("http://", "https://", "tg://"))
            )

            # اسم الزر
            label = " ".join(parts[:url_index])

            # الرابط
            url = parts[url_index]

            # اللون اختياري
            style = parts[url_index + 1] if len(parts) > url_index + 1 else None

            # الايموجي اختياري
            icon = parts[url_index + 2] if len(parts) > url_index + 2 else None

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

        except Exception as e:
            await ABH.send_message(
                wfffp,
                f"حدث خطأ في الأزرار: {e}"
            )

    if row:
        buttons.append(row)

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
