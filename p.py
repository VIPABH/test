from ABH import ABH, events, bot_token
import json, pytz, asyncio, os, sys
from datetime import datetime
from code import *
async def run_cmd(command: str):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode().strip(), stderr.decode().strip(), process.returncode
@ABH.on(events.NewMessage(pattern="^تحديث$", from_users=[1910015590]))
async def update_repo(event):
    stdout, stderr, code = await run_cmd("git pull")
    if code == 0:
        await event.reply(f" تحديث السورس بنجاح")
        os.execv(sys.executable, [sys.executable, "p.py"])
    else:
        await event.reply(f" حدث خطأ أثناء التحديث:\n\n{stderr}")
@ABH.on(events.NewMessage(pattern=r'^ارسل الملفات$', from_users=[1910015590]))
async def send_all_files(event):
    try:
        folder_path = "."
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if not files:
            await event.reply("❗️لا توجد ملفات متاحة للإرسال في المجلد.")
            return
        await event.reply(f"📤 جارٍ إرسال {len(files)} ملفًا، يرجى الانتظار...")
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            await ABH.send_file(event.chat_id, file=file_path)
        await event.reply("✅ تم إرسال جميع الملفات بنجاح.")
    except Exception as e:
        await event.reply(f"حدث خطأ أثناء إرسال الملفات: {e}")
@ABH.on(events.NewMessage(pattern=r'^ارسل ملف (.+)$', from_users=[1910015590]))
async def send_file(event):
    file_name = event.pattern_match.group(1)
    if not os.path.exists(file_name):
        return await event.reply("❗️الملف غير موجود.")
    await event.reply("📤 جاري ارسال الملف...")
    await ABH.send_file(event.chat_id, file=file_name)
@ABH.on(events.NewMessage(pattern=r'^حذف ملف (.+)$', from_users=[1910015590]))
async def delete_file(event):
    file_name = event.pattern_match.group(1)
    if not os.path.exists(file_name):
        return await event.reply("الملف غير موجود.")
    os.remove(file_name)
    await event.reply("✅ تم حذف الملف بنجاح.")
@ABH.on(events.NewMessage(pattern=r'^الملفات$', from_users=[1910015590]))
async def list_files(event):
    files = os.listdir('.')
    if not files:
        return await event.reply("❗️لا توجد ملفات في المجلد الحالي.")
    file_list = "\n" .join(files)
    await event.reply(f"📂 قائمة الملفات\n{file_list}")
def main():
    print("config is starting...")
    ABH.start(bot_token=bot_token)
    ABH.run_until_disconnected()
if __name__ == "__main__":
    main()
