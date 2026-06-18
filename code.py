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
async def monitor_guests(e):
    guest_info = getattr(e.message, 'guestchat_via_from', None)
    
    if guest_info is not None:
        # إذا كان الكائن PeerUser، نستخدم .user_id بدلاً من .id
        # نستخدم getattr كإجراء احترازي إذا تغير نوع الكائن مستقبلاً
        guest_id = getattr(guest_info, 'user_id', getattr(guest_info, 'id', None))
        
        bot_id = e.client.me.id
        
        alert = (
            f"⚠️ **نشاط ضيف جديد مكتشف**\n\n"
            f"🆔 **ID الشخص:** `{guest_id}`\n"
            f"🤖 **ID البوت المشغل:** `{bot_id}`"
        )
        
        await e.reply(alert)
