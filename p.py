import os
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from asyncio import sleep  # استخدام sleep لتحديد التأخير بين التفاعلات

wffp = 1910015590  # معرف المستخدم المستهدف
accounts = []
session_configs = [
    {"session": "session_1", "api_id": int(os.getenv("API_ID")), "api_hash": os.getenv("API_HASH")},
    {"session": "session_2", "api_id": int(os.getenv("API_ID_2")), "api_hash": os.getenv("API_HASH_2")},
    {"session": "session_3", "api_id": int(os.getenv("API_ID_3")), "api_hash": os.getenv("API_HASH_3")},
    {"session": "session_4", "api_id": int(os.getenv("API_ID_4")), "api_hash": os.getenv("API_HASH_4")},
    {"session": "session_5", "api_id": int(os.getenv("API_ID_5")), "api_hash": os.getenv("API_HASH_5")},
    {"session": "session_6", "api_id": int(os.getenv("API_ID_6")), "api_hash": os.getenv("API_HASH_6")},
]

# إعداد الجلسات
for conf in session_configs:
    accounts.append(TelegramClient(conf["session"], conf["api_id"], conf["api_hash"]))

target_user_id = None
selected_emojis = []

# إضافة الأحداث للعملاء
for client in accounts:
    @client.on(events.NewMessage(pattern=r'^ازعاج\s+(.+)$'))
    async def set_target_user_with_reaction(event):
        global target_user_id, selected_emojis
        uid = event.sender_id
        if event.is_reply and uid == wffp:
            reply_msg = await event.get_reply_message()
            target_user_id = reply_msg.sender_id
            emojis_str = event.pattern_match.group(1).strip()
            # تحويل الرموز التعبيرية إلى قائمة نصية من الرموز التعبيرية
            selected_emojis = [e.strip() for e in emojis_str.split() if e.strip()]
            print(f"تم تحديد {target_user_id} للتفاعل التلقائي باستخدام: {' '.join(selected_emojis)}")

    @client.on(events.NewMessage(pattern=r'^الغاء ازعاج$'))
    async def cancel_auto_react(event):
        global target_user_id, selected_emojis
        target_user_id = None
        selected_emojis = []
        print("تم إلغاء نمط الإزعاج.")

    @client.on(events.NewMessage())
    async def auto_react(event):
        if target_user_id and event.sender_id == target_user_id and selected_emojis:
            try:
                for emoji in selected_emojis:
                    # إرسال التفاعل مع الرموز التعبيرية النصية مباشرة
                    await client(SendReactionRequest(
                        peer=event.chat_id,
                        msg_id=event.id,
                        reaction=emoji  # التفاعل باستخدام الرموز التعبيرية النصية
                    ))
                    print(f"\u2705 تم التفاعل مع الرسالة {event.id} باستخدام: {emoji}")
                    await sleep(5)  # تأخير بين التفاعلات
            except Exception as e:
                print(f"\u26a0\ufe0f فشل التفاعل مع الرسالة {event.id}: {e}")

# بدء الجلسات
for client in accounts:
    client.start()

print("\u2705 تم تشغيل جميع الجلسات بنجاح. استخدم 'ازعاج + الرموز' بالرد على رسالة لتفعيل النمط.")

from asyncio import get_event_loop, gather
loop = get_event_loop()
loop.run_until_complete(gather(*[client.run_until_disconnected() for client in accounts]))
