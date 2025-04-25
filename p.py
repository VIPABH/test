import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

accounts = []
session_configs = [
    {"session": "session", "api_id": int(os.getenv("API_ID")), "api_hash": os.getenv("API_HASH")},
    {"session": "session_2", "api_id": int(os.getenv("API_ID_2")), "api_hash": os.getenv("API_HASH_2")},
    {"session": "session_3", "api_id": int(os.getenv("API_ID_3")), "api_hash": os.getenv("API_HASH_3")},
    {"session": "session_4", "api_id": int(os.getenv("API_ID_4")), "api_hash": os.getenv("API_HASH_4")},
    {"session": "session_5", "api_id": int(os.getenv("API_ID_5")), "api_hash": os.getenv("API_HASH_5")},
    {"session": "session_6", "api_id": int(os.getenv("API_ID_6")), "api_hash": os.getenv("API_HASH_6")},
]

# تخزين حالة كل عميل بشكل منفصل
client_states = {}

# إنشاء الحسابات وتخزين الحالة الافتراضية
for conf in session_configs:
    client = TelegramClient(conf["session"], conf["api_id"], conf["api_hash"])
    accounts.append(client)
    client_states[client] = {
        "target_user_id": None,
        "selected_emojis": []
    }

# أوامر الإدارة
async def set_target_user_with_reaction(event):
    client = event.client
    state = client_states[client]
    uid = event.sender_id
    if event.is_reply and uid == 1910015590:
        reply_msg = await event.get_reply_message()
        state["target_user_id"] = reply_msg.sender_id
        emojis_str = event.pattern_match.group(1).strip()
        state["selected_emojis"] = [ReactionEmoji(emoticon=e.strip()) for e in emojis_str if e.strip()]
        print(f"تم تحديد {state['target_user_id']} للتفاعل التلقائي باستخدام: {' '.join(e.emoticon for e in state['selected_emojis'])}")
    else:
        await event.respond("\u2757 يجب الرد على رسالة المستخدم الذي تريد إزعاجه باستخدام الأمر: `ازعاج + الرموز`")

async def cancel_auto_react(event):
    client = event.client
    state = client_states[client]

    state["target_user_id"] = None
    state["selected_emojis"] = []


    print("تم إلغاء نمط الإزعاج لهذا العميل.")

async def auto_react(event):
    client = event.client
    state = client_states[client]

    if state["target_user_id"] and event.sender_id == state["target_user_id"] and state["selected_emojis"]:
        try:
            await client(SendReactionRequest(
                peer=event.chat_id,
                msg_id=event.id,
                reaction=state["selected_emojis"]
            ))
            print(f"\u2705 تم التفاعل مع الرسالة {event.id} باستخدام الرموز: {' '.join(e.emoticon for e in state['selected_emojis'])}")
        except Exception as e:
            print(f"\u26a0\ufe0f فشل التفاعل مع الرسالة {event.id}: {e}")

# بدء الجلسات
async def start_clients():
    print("بدء الجلسات...")

    for client in accounts:
        client.add_event_handler(set_target_user_with_reaction, events.NewMessage(pattern=r'^ازعاج\s+(.+)$'))
        client.add_event_handler(cancel_auto_react, events.NewMessage(pattern=r'^الغاء ازعاج$'))
        client.add_event_handler(auto_react, events.NewMessage())

    for client in accounts:
        await client.start()

    print("\u2705 تم تشغيل جميع الجلسات بنجاح.")
    await asyncio.gather(*(client.run_until_disconnected() for client in accounts))

# تشغيل الجلسات
asyncio.run(start_clients())
