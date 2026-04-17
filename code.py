from telethon import events, Button, types
from ABH import ABH

@ABH.on(events.NewMessage(pattern=r"^(ازرار|تحكم|طلب)$"))
async def send_all_types(event):
    await event.respond(
        "✨ **لوحة التحكم الشاملة (حل يدوي)**\nإختر نوع الزر:",
        buttons=[
            # أزرار Callback عادية (تعمل في كل الإصدارات)
            [
                Button.inline("تفعيل ✅", data=b"color_on"),
                Button.inline("حذف 🗑️", data=b"color_off")
            ],
            # حل يدوي لزر اختيار القناة/المستخدم (تجاوز نقص Button.request_peer)
            [
                Button.inline("إرسال رابط قناة 📢", data=b"send_channel"),
                Button.inline("إرسال رابط مستخدم 👤", data=b"send_user")
            ],
            # أزرار الروابط
            [
                Button.url("رابط خارجي 🌐", "https://t.me/Python")
            ]
        ]
    )

# معالجة ضغطات الأزرار
@ABH.on(events.CallbackQuery)
async def callback_handler(event):
    if event.data == b"color_on":
        await event.answer("تم التفعيل بنجاح! 🟢", alert=True)
    
    elif event.data == b"color_off":
        await event.edit("⚠️ تم إخفاء الأزرار.")
    
    # محاكاة لطلب البيانات إذا لم يعمل الزر التلقائي
    elif event.data in [b"send_channel", b"send_user"]:
        await event.answer("يرجى إرسال أيدي (ID) الجهة المطلوبة في الرسالة القادمة..", alert=True)

# الاستماع لتحديثات الخام (Raw) بشكل صحيح وتجنب UpdateIdResult
@ABH.on(events.Raw)
async def raw_handler(event):
    # نستخدم النوع العام UpdateNewMessage للبحث عن "أحداث الأزرار"
    if isinstance(event, types.UpdateNewMessage):
        msg = event.message
        # التحقق من وجود "Action" داخل الرسالة (وهو ما يرسله زر request_peer)
        if hasattr(msg, 'action') and msg.action:
            # نوع الأكشن عند اختيار مستخدم أو قناة
            if isinstance(msg.action, types.MessageActionRequestedPeerSent):
                peer = msg.action.peers[0]
                peer_id = getattr(peer, 'user_id', getattr(peer, 'channel_id', getattr(peer, 'chat_id', 'Unknown')))
                await ABH.send_message(msg.peer_id, f"✅ تم استلام الهوية بنجاح!\nالأيدي المختار هو: `{peer_id}`")
