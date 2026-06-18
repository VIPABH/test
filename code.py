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
@ABH.on(events.NewMessage)
async def detect_guest_flow(e):
    # التحقق من وجود نشاط ضيف
    if e.message.guestchat_via_from:
        guest_id = e.message.guestchat_via_from.user_id
        sender_id = e.sender_id
        
        # تنبيه فوري لك في الخاص
        alert = (
            f"⚠️ **تم كشف تدفق وكيلي!**\n"
            f"👤 المرسل (البوت/المخرب): {sender_id}\n"
            f"👤 الوكيل (الضيف): {guest_id}\n"
            f"🔗 هذا يعني أنهم يعملون معاً الآن!"
        )
        await e.reply(alert)
        
        # يمكنك هنا إضافة كود للحظر التلقائي للطرفين إذا أردت
