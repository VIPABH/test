from telethon import events, Button, types
from ABH import ABH

# 1. إرسال الأزرار (إزالة style لأن Telethon 1.x لا يدعمها في Button.inline)
@ABH.on(events.NewMessage(pattern=r"^(ازرار|تحكم|طلب)$"))
async def send_all_types(event):
    await event.respond(
        "✨ **لوحة التحكم الشاملة**\nإختر نوع الزر الذي تود اختباره:",
        buttons=[
            # أزرار تفاعلية (الألوان تعتمد على الإيموجي في هذا الإصدار)
            [
                Button.inline("تفعيل ✅", data=b"color_on"),
                Button.inline("حذف 🗑️", data=b"color_off")
            ],
            # أزرار اختيار الجهات (تستخدم PeerType ككائنات وليس نصوص)
            [
                Button.request_peer("اختيار قناة 📢", request_id=1, peer_type=types.RequestPeerTypeChannels()),
                Button.request_peer("اختيار مستخدم 👤", request_id=2, peer_type=types.RequestPeerTypeUsers())
            ],
            # أزرار الخدمات
            [
                Button.url("رابط خارجي 🌐", "https://t.me/Python"),
                Button.inline("معلومات ℹ️", data=b"info")
            ]
        ]
    )

# 2. الاستماع لضغطات الأزرار
@ABH.on(events.CallbackQuery)
async def callback_handler(event):
    if event.data == b"color_on":
        await event.answer("تم التفعيل بنجاح! 🟢", alert=True)
    elif event.data == b"color_off":
        await event.edit("⚠️ تم إلغاء تفعيل الأزرار.")

# 3. تصحيح خطأ AttributeError: الاستماع لنتائج الاختيار
@ABH.on(events.Raw)
async def peer_result_handler(event):
    # في Telethon، الحدث الصحيح لاستلام نتيجة الزر هو UpdatePeerSettings أو التحديث العام
    # هنا نتحقق من وصول تحديث يحتوي على معلومات المستخدم المختار
    if isinstance(event, types.UpdateNewMessage):
        msg = event.message
        if msg.action and isinstance(msg.action, types.MessageActionRequestedPeerSent):
            peer_id = msg.action.peers[0].user_id if hasattr(msg.action.peers[0], 'user_id') else msg.action.peers[0].channel_id
            await ABH.send_message(msg.peer_id, f"✅ تم استلام الهوية بنجاح!\nالأيدي المختار: `{peer_id}`")
