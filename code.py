from telethon import events, Button
from Resources import *
from ABH import ABH

ITEMS_PER_PAGE = 50
pages_db = {}

async def render_page(client, chat_id, user_id, page_number):
    start = page_number * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = list(لطميات.items())[start:end]
    msg = ""
    for name, data in page_items:
        msg += f"- `{name}`\n"
    buttons = [
        [
            Button.inline("◀️ السابق", data=f"back:{page_number}"),
            Button.inline("▶️ التالي", data=f"next:{page_number}")
        ]
    ]
    msg_id = pages_db[chat_id][user_id]["msg_id"]
    await client.edit_message(chat_id, msg_id, msg, buttons=buttons)
    pages_db[chat_id][user_id]["page"] = page_number
@ABH.on(events.NewMessage(pattern='^لطميات$', from_users=[wfffp]))
async def listlatmeat(e):
    chat_id = e.chat_id
    user_id = e.sender_id
    msg = await e.reply("جاري التحميل...")
    if chat_id not in pages_db:
        pages_db[chat_id] = {}
    pages_db[chat_id][user_id] = {
        "page": 0,
        "msg_id": msg.id
    }
    await render_page(ABH, chat_id, user_id, 0)
@ABH.on(events.CallbackQuery)
async def callbacklet(e):
    chat_id = e.chat_id
    user_id = e.sender_id
    data = e.data.decode("utf-8")
    if chat_id not in pages_db or user_id not in pages_db[chat_id]:
        await e.answer()
        return
    if data.startswith("next:"):
        current = int(data.split(":")[1])
        await e.answer()
        await render_page(ABH, chat_id, user_id, current + 1)
    elif data.startswith("back:"):
        current = int(data.split(":")[1])
        if current == 0:
            await e.answer()
            return
        await e.answer()
        await render_page(ABH, chat_id, user_id, current - 1)
