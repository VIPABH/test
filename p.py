import os
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

# إعداد الاتصال
api_id = int(os.getenv("API_ID_2"))
api_hash = os.getenv("API_HASH_2")
session_name = "session"
client = TelegramClient(session_name, api_id, api_hash)

target_user_id = None
selected_emojis = []


@client.on(events.NewMessage(pattern=r'^/ازعاج\s+(.+)$'))
async def set_target_user_with_reaction(event):
    global target_user_id, selected_emojis

    if event.is_reply:
        reply_msg = await event.get_reply_message()
        target_user_id = reply_msg.sender_id

        # استخراج الرموز التعبيرية وفصلها (بمسافة أو بدون)
        emojis_str = event.pattern_match.group(1).strip()
        selected_emojis = [ReactionEmoji(emoticon=e.strip()) for e in emojis_str if e.strip()]

        await event.respond(f"✅ تم تفعيل نمط الإزعاج على المستخدم `{target_user_id}` باستخدام الرموز: {' '.join(e.emoticon for e in selected_emojis)}")
        print(f"تم تحديد {target_user_id} للتفاعل التلقائي باستخدام: {' '.join(e.emoticon for e in selected_emojis)}")
    else:
        await event.respond("❗ يجب الرد على رسالة المستخدم الذي تريد إزعاجه باستخدام الأمر: `ازعاج + 🍓🍌🌟` (يمكنك وضع أكثر من رمز)")

@client.on(events.NewMessage(pattern=r'^الغاء ازعاج$'))
async def cancel_auto_react(event):
    global target_user_id, selected_emojis

    target_user_id = None
    selected_emojis = []

    await event.respond("🛑 تم إيقاف نمط الإزعاج. لن يتم التفاعل مع أي رسائل حالياً.")
    print("تم إلغاء نمط الإزعاج.")

@client.on(events.NewMessage())
async def auto_react(event):
    if target_user_id and event.sender_id == target_user_id and selected_emojis:
        try:
            await client(SendReactionRequest(
                peer=event.chat_id,
                msg_id=event.id,
                reaction=selected_emojis
            ))
            print(f"✅ تم التفاعل مع الرسالة {event.id} باستخدام الرموز: {' '.join(e.emoticon for e in selected_emojis)}")
        except Exception as e:
            print(f"⚠️ فشل التفاعل مع الرسالة {event.id}: {e}")

client.start()
print("✅ البوت جاهز. استخدم الأمر 'ازعاج + 🍓🍌🌟' بالرد على رسالة لتفعيل الإزعاج أو 'الغاء ازعاج' للإيقاف.")
client.run_until_disconnected()
