from ABH import *
@ABH.on(events.NewMessage(pattern=r"^زر(?:\s+(.+))?$"))
async def handler(event):

    if not event.is_group:
        return

    full_text = event.pattern_match.group(1)

    if not full_text:
        return await event.reply(
            "يرجى كتابة الأزرار بالصيغة:\n\n"
            "`اسم الزر \\ الرابط \\ اللون \\ الايموجي`\n\n"
            "مثال:\n"
            "`زر المطور \\ https://t.me/k_4x1 \\ ازرق \\ 🌚`\n\n"
            "ويمكن إضافة أكثر من زر بفصلهم بـ `|`"
        )

    if not event.is_reply:
        return await event.reply(
            "يجب الرد على الرسالة التي تريد نسخها."
        )

    items = [
        item.strip()
        for item in full_text.split("|")
        if "\\" in item
    ]

    if not items:
        return await event.reply(
            "تأكد من كتابة الأزرار بصيغة:\n"
            "`اسم الزر \\ الرابط \\ اللون \\ الايموجي`"
        )

    reply_msg = await event.get_reply_message()

    buttons = []
    row = []

    for item in items:
        try:
            parts = [x.strip() for x in item.split("\\")]

            if len(parts) < 2:
                continue

            label = parts[0]
            url = parts[1]

            # اللون
            color = parts[2] if len(parts) >= 3 else ""

            # الإيموجي
            emoji = parts[3] if len(parts) >= 4 else ""

            # إضافة الإيموجي إلى اسم الزر
            if emoji:
                label = f"{emoji} {label}"

            # اللون يتم قراءته هنا
            # Telegram لا يسمح بتغيير لون Button.url
            # لذلك نخليه محفوظًا بدون أن يؤثر على الزر حاليًا
            button = Button.url(label, url)

            row.append(button)

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
