import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import InputReportReasonPersonalDetails

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = 'session'  # اسم ملف الجلسة

TARGET_USERNAME = "kasmalshatbust"
TARGET_MSG_IDS = [41, 47, 73]

client = TelegramClient(SESSION, API_ID, API_HASH)

async def send_reports():
    target = await client.get_entity(TARGET_USERNAME)
    success = 0
    fail = 0

    for i in range(1000):  # عدد البلاغات المطلوب إرسالها
        for msg_id in TARGET_MSG_IDS:
            try:
                await client(ReportRequest(
                    peer=target,
                    id=[msg_id],
                    reason=InputReportReasonPersonalDetails(),
                    message=f"انتهاك معلومات شخصية في الرسالة {msg_id}"
                ))
                success += 1
                await asyncio.sleep(0.3)  # وقت انتظار بين البلاغات لتفادي الحظر
            except Exception as e:
                fail += 1
                print(f"فشل في البلاغ رقم {i+1} على الرسالة {msg_id}: {e}")
    return success, fail

@client.on(events.NewMessage(pattern=r'/ابلاغ'))
async def handler(event):
    await event.respond("⏳ جارٍ إرسال البلاغات، الرجاء الانتظار ...")
    success, fail = await send_reports()
    me = await client.get_me()
    await event.respond(
        f"✅ تم إرسال {success} بلاغات بنجاح بسبب (معلومات شخصية) على @{TARGET_USERNAME}.\n"
        f"❌ فشل في إرسال {fail} بلاغ.\n"
        f"حسابك: {me.id}"
    )

async def main():
    await client.start()
    print("Userbot started. Listening for commands...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
