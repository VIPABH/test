import os, random
from telethon import TelegramClient, events
from faster_whisper import WhisperModel
from ABH import *
from Resources import *
from telethon import types, events

@ABH.on(events.NewMessage(pattern='/test'))
async def send_clean(e):
    # 1. النص المجرد تماماً بدون أي وسوم أو أكواد
    text = "المستخدم ( Anymous ) ما عنده قيود ⬆️"
    
    # 2. تحديد مكان المنشن بدقة (يبدأ من الحرف رقم 11 وطوله 7 أحرف)
    mention_entity = types.MessageEntityMentionName(
        offset=11,      # بداية الاسم داخل النص
        length=7,       # طول الاسم (Anymous)
        user_id=7908156943
    )
    
    # 3. تحديد مكان الإيموجي المميز (مكانه في آخر النص وطوله 2 حرف لأنه سهم)
    emoji_entity = types.MessageEntityCustomEmoji(
        offset=35,      # مكان السهم ⬆️ في النص
        length=2,       # طول الرمز
        document_id=5372913502140766965 # آيدي الإيموجي المميز
    )
    
    # 4. إرسال الرسالة مع تمرير الـ entities
    await e.reply(text, formatting_entities=[mention_entity, emoji_entity])
