from telethon import events, Button, types
# تأكد من أن ملف ABH يحتوي على تعريف كائن البوت/Client باسم ABH
from ABH import ABH 

# 1. إرسال الأزرار (تم تصحيح Regex بإضافة ^ و $ و | )
@ABH.on(events.NewMessage(pattern=r"^(ازرار|تحكم|طلب)$"))
async def send_all_types(event):
    await event.respond(
        "✨ **لوحة التحكم الشاملة (تحديث 2026)**\n"
        "اختر نوع الزر الذي تود اختباره:",
        buttons=[
            # أزرار ملونة (Style)
            [
                Button.inline("تفعيل (أخضر) ✅", data=b"color_on", style="success"),
                Button.inline("حذف (أحمر) 🗑️", data=b"color_off", style="danger")
            ],
            # أزرار اختيار الجهات (Peer Selectors)
            [
                Button.request_peer("اختيار قناة 📢", request_id=1, peer_type='channel'),
                Button.request_peer("اختيار مستخدم 👤", request_id=2, peer_type='user')
            ],
            # أزرار الخدمات والروابط
            [
                Button.buy("شراء نجوم ⭐"),
                Button.url("رابط خارجي 🌐", "https://t.me/Python")
            ]
        ]
    )

# 2. الاستماع لضغطات الأزرار (Callback Query)
@ABH.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data
    if data == b"color_on":
        await event.answer("تم التفعيل باللون الأخضر! 🟢", alert=True)
    elif data == b"color_off":
        # حذف الأزرار وتعديل النص
        await event.edit("⚠️ **تم تنفيذ أمر الحذف بنجاح.**", buttons=None)

# 3. الاستماع لنتائج اختيار (قناة/مستخدم)
@ABH.on(events.Raw)
async def peer_result_handler(event):
    # التعامل مع نتيجة اختيار المستخدم/القناة
    if isinstance(event, types.UpdateIdResult):
        peer_id = event.id
        # نرسل رسالة للدردشة التي تم فيها الاختيار
        await ABH.send_message(event.chat_id, f"✅ **تم استلام المعرف بنجاح!**\nالأيدي المختار: `{peer_id}`")

# 4. معالجة أوامر الشراء (Stars)
@ABH.on(events.Raw)
async def payment_handler(event):
    if isinstance(event, types.UpdateBotPrecheckoutQuery):
        # الموافقة على عملية الدفع بالنجوم قبل إتمامها
        from telethon.tl.functions.messages import SetBotPrecheckoutResultsRequest
        await ABH(SetBotPrecheckoutResultsRequest(
            query_id=event.query_id,
            success=True
        ))
