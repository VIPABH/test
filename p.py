import os
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import InputReportReasonPersonalDetails

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION_NAME") or "user"

TARGET_USERNAME = "kasmalshatbust"
TARGET_MSG_IDS = [41, 47, 73]

client = TelegramClient(SESSION, API_ID, API_HASH)

async def report_messages():
    await client.start()
    me = await client.get_me()
    await client.send_message("me", f"📣تم البدء}")

    try:
        target = await client.get_entity(TARGET_USERNAME)
        success = 0

        for msg_id in TARGET_MSG_IDS:
            try:
                await client(ReportRequest(
                    peer=target,
                    id=[msg_id],
                    reason=InputReportReasonPersonalDetails(),
                    message=f"انتهاك معلومات شخصية في الرسالة {msg_id}"
                ))
                print(f"✅ تم التبليغ عن الرسالة {msg_id}")
                success += 1
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"❌ فشل في الرسالة {msg_id}: {e}")
        
        me = await client.get_me()
        await client.send_message("me", f"📣 تم إرسال {success} بلاغات بسبب (معلومات شخصية) على @{TARGET_USERNAME}.\nحسابك: {me.id}")

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(report_messages())
