from telethon import events
from telethon.tl import types  
from ABH import *
# @ABH.on(events.NewMessage(pattern="تيست"))
# async def test(e):
#     # إرسال رسالة أولية للمستخدم توضح أن العملية بدأت
#     status_msg = await e.reply("جاري فحص الرسائل، يرجى الانتظار...")
    
#     # تحديد نطاق المعرفات
#     ids = list(range(502, 633)) 
    
#     # جلب الرسائل
#     messages = await ABH.get_messages("x04ou", ids=ids)
    
#     found = 0
#     deleted = 0
    
#     # فرز الرسائل
#     for msg in messages:
#         if msg is not None:
#             found += 1
#         else:
#             deleted += 1
            
#     # تحديث النتيجة للمستخدم
#     await status_msg.edit(
#         f"✅ **تم فحص الرسائل:**\n\n"
#         f"📌 **الرسائل الموجودة:** {found}\n"
#         f"🗑 **الرسائل المحذوفة:** {deleted}\n"
#         f"📊 **إجمالي النطاق:** {len(ids)}"
#     )
from telethon import TelegramClient, events

@ABH.on(events.NewMessage)
async def handler(e):
    # 1. نظام الإنذار (Alert System) - فقط للتنبيه
    alert_msg = ""
    
    # التنبيه عن البوتات الضيفة (Guest Bots)
    if e.via_bot_id:
        alert_msg += f"⚠️ تنبيه: تم رصد بوت ضيف (ID: {e.via_bot_id})\n"
    
    # التنبيه عن المنشنات (Mentions)
    if e.entities:
        for entity in e.entities:
            if isinstance(entity, (events.MessageEntityMention, events.MessageEntityMentionName)):
                mentioned = e.raw_text[entity.offset:entity.offset + entity.length]
                alert_msg += f"📢 تنبيه: منشن لبوت/مستخدم: {mentioned}\n"

    # إذا وجدنا شيئاً مشبوهاً، نرسل التنبيه أولاً
    if alert_msg:
        await e.reply(f"--- 🛡️ تقرير أمني ---\n{alert_msg}")

    # 2. عملية الالتقاط (Capture) - يعرض تفاصيل الرسالة كاملة
    text_to_reply = str(e)
    limit = 4000
    parts = [text_to_reply[i:i + limit] for i in range(0, len(text_to_reply), limit)]
    
    for part in parts:
        await e.reply(part)
