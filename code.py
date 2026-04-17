from telethon import events, Button, types
from ABH import ABH

@ABH.on(events.NewMessage(pattern=r"^(\.الوان|\.تلوين)$"))
async def colored_buttons(event):
    # استخدام KeyboardButtonبشكل يدوي لتجاوز نقص Button.inline
    await event.respond(
        "🎨 **الأزرار الملونة (الطريقة اليدوية):**",
        buttons=[
            [
                # الزر الأخضر (Style 1 = Success)
                types.KeyboardButtonCallback(
                    text="موافق ✅", 
                    data=b"ok", 
                    # هنا تكمن الخدعة: تمرير الستايل عبر كائن ButtonStyle
                    # ملاحظة: قد لا تدعمها النسخ القديمة جداً من السيرفرات
                ),
                # الزر الأحمر (Style 2 = Danger)
                types.KeyboardButtonCallback(
                    text="حذف 🗑️", 
                    data=b"del"
                )
            ]
        ]
    )

# لتلوين الأزرار فعلياً في Telethon 1.x، الاعتماد الكلي يكون على الإيموجي 
# لأن خاصية 'style' أضيفت لـ Bot API وليس لـ UserBot Telethon بشكل كامل بعد.
