from telethon import events
from ABH import ABH
from telethon.tl.types import DocumentAttributeAudio
import asyncio
from collections import defaultdict

@ABH.on(events.NewMessage(pattern="/scan_dups"))
async def scan_duplicates(event):
    channel = 'x04ou'
    seen_files = defaultdict(list)  # {file_name: [msg_id1, msg_id2, ...]}
    similar_files = defaultdict(list)

    await event.reply("🔎 جاري فحص الرسائل الصوتية بحثًا عن الملفات المتكررة...")

    for i in range(1, 386):
        try:
            msg = await ABH.get_messages(channel, ids=i)
            if not msg or not msg.document:
                continue

            # تأكد أنه ملف صوتي وليس voice
            is_audio = any(
                isinstance(attr, DocumentAttributeAudio) and not attr.voice
                for attr in msg.document.attributes
            )
            if not is_audio:
                continue

            name = msg.file.name or "unknown"

            # فحص التكرار بالاسم الكامل
            seen_files[name].append(msg.id)

            # فحص التشابه الجزئي (كلمات متشابهة مثلاً بدون الامتداد)
            name_key = name.split('.')[0].lower()
            similar_files[name_key].append(msg.id)

            await asyncio.sleep(0.2)

        except Exception:
            continue

    # الرد على الملفات المتكررة بالاسم الكامل
    duplicates = {k: v for k, v in seen_files.items() if len(v) > 1}
    similar = {k: v for k, v in similar_files.items() if len(v) > 1}

    if duplicates:
        await event.reply("📁 الملفات المتكررة (اسم مطابق تمامًا):")
        for name, ids in duplicates.items():
            links = "\n".join(
                [f"https://t.me/c/{str(msg.chat_id)[4:]}/{msg_id}" for msg_id in ids]
            )
            await event.reply(f"📄 `{name}`\n{links}")
            await asyncio.sleep(1)

    if similar:
        await event.reply("🌀 الملفات المتشابهة (اسم جزئي):")
        for key, ids in similar.items():
            if key in duplicates:
                continue  # تم إرساله بالفعل
            links = "\n".join(
                [f"https://t.me/c/{str(event.chat_id)[4:]}/{msg_id}" for msg_id in ids]
            )
            await event.reply(f"🔸 `{key}` (تشابه جزئي)\n{links}")
            await asyncio.sleep(1)

    if not duplicates and not similar:
        await event.reply("✅ لم يتم العثور على ملفات مكررة أو متشابهة.")

