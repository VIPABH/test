import os
import re
from telethon import TelegramClient, events, functions, types
from faster_whisper import WhisperModel
from ABH import *
from Resources import *

# ====================================================================
# 1. الـ Handler الأول: طباعة الـ ID الخاص بالتفاعل المخصص عند استقباله
# ====================================================================
@ABH.on(events.MessageReactionsUpdate())
async def catch_reaction_id(event):
    # نتحقق من وجود تفاعلات جديدة في التحديث
    if event.reactions:
        for r in event.reactions.results:
            # التحقق إذا كان التفاعل من نوع إيموجي مخصص
            if isinstance(r.reaction, types.ReactionCustomEmoji):
                emoji_id = r.reaction.document_id
                print(f"\n[🔥] تم رصد إيموجي مخصص!")
                print(f"Chat ID: {event.chat_id}")
                print(f"Message ID: {event.msg_id}")
                print(f"Custom Emoji ID: {emoji_id}\n")


# ====================================================================
# 2. الـ Handler الثاني: أمر يستقبل الـ ID ويحاول عمل تفاعل به
# ====================================================================
@ABH.on(events.NewMessage(pattern=r'^/react (\d+)'))
async def try_custom_reaction(event):
    # استخراج الـ ID من الأمر باستخدام الـ Regex
    emoji_id_str = event.pattern_match.group(1)
    CUSTOM_EMOJI_ID = int(emoji_id_str)
    
    # سنقوم بالتفاعل على نفس رسالة الأمر التي أرسلها المستخدم
    target_msg_id = event.id
    
    print(f"[⏳] محاولة إرسال التفاعل بالـ ID: {CUSTOM_EMOJI_ID}...")
    
    try:
        await ABH(functions.messages.SendReactionRequest(
            peer=event.chat_id,
            msg_id=target_msg_id,
            reaction=[
                types.ReactionCustomEmoji(
                    document_id=CUSTOM_EMOJI_ID
                )
            ]
        ))
        print("[✅] تم إرسال التفاعل بنجاح دون اعتراض السيرفر!")
        await event.reply("✅ تم إرسال التفاعل المخصص بنجاح!")
        
    except Exception as e:
        print(f"[❌] فشل إرسال التفاعل. السبب من السيرفر: {e}")
        await event.reply(f"❌ فشل السيرفر في قبول التفاعل:\n`{e}`")
