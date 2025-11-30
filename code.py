from telethon import events, Button
from Resources import *
from ABH import ABH

# عدد العناصر في كل صفحة
ITEMS_PER_PAGE = 50

# دالة تعرض صفحة اللطميات
async def render_page(e, page_number):
    start = page_number * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE

    # استخراج الصفحة المطلوبة
    page_items = list(لطميات.items())[start:end]

    if not page_items:
        await e.edit("لا توجد بيانات إضافية.")
        return

    # بناء النص
    msg = ""
    for name, data in page_items:
        msg += f"- `{name}`\n"

    # أزرار التنقّل تحمل رقم الصفحة القادمة
    buttons = [
        [
            Button.inline("◀️ السابق", data=f"back:{page_number}"),
            Button.inline("▶️ التالي", data=f"next:{page_number}")
        ]
    ]

    # تعديل الرسالة الحالية
    await e.reply(msg, buttons=buttons)


# أوّل رسالة: الصفحة 0
@ABH.on(events.NewMessage(pattern='^لطميات$', from_users=[wfffp]))
async def listlatmeat(e):
    await render_page(e.message, 0)


# مستمع الأزرار
@ABH.on(events.CallbackQuery)
async def callbacklet(e):
    data = e.data.decode("utf-8")

    # زر التالي
    if data.startswith("next:"):
        current_page = int(data.split(":")[1])
        await e.answer()
        await render_page(e, current_page + 1)

    # زر السابق
    elif data.startswith("back:"):
        current_page = int(data.split(":")[1])
        await e.answer()

        if current_page == 0:
            await e.answer("لا توجد صفحة سابقة.", alert=False)
            return

        await render_page(e, current_page - 1)
