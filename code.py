from telethon import events, Button

# 1. قائمة الأوامر التي يرسل البوت بناءً عليها الأزرار
@ABH.on(events.NewMessage(pattern=r"^\(ازرار|تحكم|طلب)$"))
async def send_all_types(event):
    await event.respond(
        "✨ **لوحة التحكم الشاملة**\nإختر نوع الزر الذي تود اختباره:",
        buttons=[
            # أزرار ملونة
            [
                Button.inline("تفعيل (أخضر) ✅", data=b"color_on", style="success"),
                Button.inline("حذف (أحمر) 🗑️", data=b"color_off", style="danger")
            ],
            # أزرار الاختيار (Peer Selectors)
            [
                Button.request_peer("اختيار قناة 📢", request_id=1, peer_type='channel'),
                Button.request_peer("اختيار مستخدم 👤", request_id=2, peer_type='user')
            ],
            # أزرار الخدمات
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
        await event.edit("⚠️ **تم حذف الرسالة الأصلية واستبدالها بنص التحذير.**", buttons=None)
        await event.answer("تم تنفيذ أمر الحذف 🔴", alert=False)

# 3. الاستماع لنتائج اختيار (قناة/مستخدم) - Peer Select Result
@ABH.on(events.Raw)
async def peer_result_handler(event):
    # في إصدار 1.43.1، تليجرام ترسل تحديثاً عند اختيار مستخدم من زر RequestPeer
    if isinstance(event, events.Raw.types.UpdateIdResult):
        peer_id = event.id
        await ABH.send_message(event.chat_id, f"✅ تم استلام الهوية بنجاح!\nالأيدي المختار: `{peer_id}`")

# 4. معالجة أوامر الشراء (Stars)
@ABH.on(events.Raw)
async def payment_handler(event):
    if isinstance(event, events.Raw.types.UpdateBotPrecheckoutQuery):
        # الموافقة التلقائية على عملية الدفع بالنجوم
        await ABH(events.Raw.functions.messages.SetBotPrecheckoutResultsRequest(
            query_id=event.query_id,
            success=True
        ))
