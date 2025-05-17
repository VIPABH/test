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
    # بدء الجلسة مع دعم الإدخال التفاعلي لرقم الهاتف، الكود، وكلمة المرور
    await client.start(
        phone=lambda: input("أدخل رقم هاتفك (مثال +964770xxxxxxx): "),
        code_callback=lambda: input("أدخل كود التحقق الذي استلمته: "),
        password=lambda: input("أدخل كلمة مرور التحقق بخطوتين (إن وجدت): ")
    )
    
    me = await client.get_me()
    await client.send_message("me", "📣 تم البدء في إرسال البلاغات")

    try:
        target = await client.get_entity(TARGET_USERNAME)
        success = 0
        fail = 0

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
                await asyncio.sleep(0.5)  # لتفادي الحظر المؤقت من تيليجرام
            except Exception as e:
                print(f"❌ فشل في البلاغ على الرسالة {msg_id}: {e}")
                fail += 1
        
        await client.send_message(
            "me",
            f"📣 تم إرسال {success} بلاغات بنجاح بسبب (معلومات شخصية) على @{TARGET_USERNAME}.\n"
            f"❌ فشل في إرسال {fail} بلاغ.\n"
            f"حسابك: {me.id}"
        )

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(report_messages())
