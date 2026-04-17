from ABH import ABH  # استيراد العميل الخاص بك
from telethon import Button, events

async def send_super_buttons(event):
    await event.respond(
        "🚀 **المصنع الشامل للأزرار (تحديث 2026):**\n"
        "هذه الرسالة تجمع الأزرار الملونة، الأزرار التفاعلية، وأزرار الخدمات.",
        buttons=[
            # --- الصف الأول: أزرار ملونة (جديد 2026) ---
            [
                Button.inline("تفعيل 🟢", data=b"on", style="success"), # أخضر
                Button.inline("تعطيل 🔴", data=b"off", style="danger"),  # أحمر
            ],
            
            # --- الصف الثاني: أزرار الروابط والبيانات ---
            [
                Button.url("رابط الموقع 🌐", "https://t.me/Python"),
                Button.inline("بيانات (أزرق) 🔵", data=b"info", style="primary")
            ],
            
            # --- الصف الثالث: أزرار اختيار الجهات (Peer Selectors) ---
            [
                Button.request_peer("اختر مستخدم 👤", request_id=1, peer_type='user'),
                Button.request_peer("اختر قناة 📢", request_id=2, peer_type='channel')
            ],
            
            # --- الصف الرابع: أزرار المشاركة والبحث ---
            [
                Button.switch_inline("مشاركة 📤", query="share", same_peer=False),
                Button.switch_inline("بحث هنا 🔍", query="", same_peer=True)
            ],
            
            # --- الصف الخامس: أزرار الخدمات والنجوم ---
            [
                Button.buy("شراء بالنجوم ⭐"),
                Button.auth("دخول خارجي 🔑", url="https://example.com")
            ]
        ]
    )

# كود معالجة ضغطة الأزرار الملونة
@ABH.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data
    if data == b"on":
        await event.answer("تم التفعيل بنجاح! ✅", alert=True)
    elif data == b"off":
        await event.answer("تم التعطيل! ❌", alert=False)
