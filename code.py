from telethon import events
from ABH import *
import os
import shutil
import zipfile
import tempfile
from pathlib import Path
from analyzer import analyze_file_text, count_project_text
TELEGRAM_MAX_LEN = 4000
client = ABH
async def send_long_text(event, text: str, filename_if_long: str) -> None:
    """يبعث النص كرسالة عادية، أو كملف لو كان طويل جدًا."""
    if len(text) <= TELEGRAM_MAX_LEN:
        await event.respond(f"```\n{text}\n```")
        return

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(text)
        tmp_path = tmp.name

    await event.respond(
        "التقرير طويل، تم إرساله كملف 👇",
        file=tmp_path,
    )
    os.remove(tmp_path)


@client.on(events.NewMessage(pattern=r"/analyze"))
async def handle_analyze(event):
    reply = await event.get_reply_message()
    if not reply or not reply.file or not (reply.file.name or "").endswith(".py"):
        await event.respond(
            "استخدم الأمر كرد (reply) على رسالة فيها ملف بايثون (.py)."
        )
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = await reply.download_media(file=tmpdir)
        try:
            report = analyze_file_text(file_path)
        except SyntaxError as e:
            await event.respond(f"⚠️ خطأ في تحليل الملف: {e}")
            return

    await send_long_text(event, report, "analyze_report.txt")


@client.on(events.NewMessage(pattern=r"/count"))
async def handle_count(event):
    reply = await event.get_reply_message()
    if not reply or not reply.file or not (reply.file.name or "").endswith(".zip"):
        await event.respond(
            "استخدم الأمر كرد (reply) على رسالة فيها ملف مضغوط (.zip) للمشروع كامل."
        )
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = await reply.download_media(file=tmpdir)
        extract_dir = Path(tmpdir) / "project"
        extract_dir.mkdir()

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)
        except zipfile.BadZipFile:
            await event.respond("⚠️ الملف المرفق ليس ملف zip صالح.")
            return

        report = count_project_text(str(extract_dir))

    await send_long_text(event, report, "count_report.txt")
