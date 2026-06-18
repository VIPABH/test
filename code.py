from telethon import events
from telethon.tl import types  
from ABH import *
from telethon import events

client = ABH # تأكد أن هذا المتغير هو الـ Client الخاص بك

# سنقوم بتعريف دالة للتحقق من أن البوت تم ذكره
async def is_mentioned(event):
    # تحقق مما إذا كان هناك رد على رسالة سابقة للبوت
    if event.reply_to_msg_id:
        reply_message = await event.get_reply_message()
        if reply_message and reply_message.sender_id == (await client.get_me()).id:
            return True
    
    # تحقق مما إذا كان البوت مذكوراً في النص (@username)
    bot_username = (await client.get_me()).username
    if bot_username and f"@{bot_username}" in event.raw_text:
        return True
        
    return False

# نستخدم الحدث مع فلتر (func)
@client.on(events.NewMessage(func=is_mentioned))
async def handler(event):
    await event.reply("مرحباً! تم استدعائي في وضع الضيف.")

print("البوت يعمل الآن (سيستجيب فقط عند الإشارة إليه أو الرد عليه)...")



    
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
