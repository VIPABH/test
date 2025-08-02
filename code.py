from telethon import events, Button
from ABH import ABH as client
@client.on(events.NewMessage(pattern="/ابدأ"))
async def handler(event):
    user_id = event.sender_id
    chat_id = event.chat_id

    async def wait_reply(new_event):
        if new_event.chat_id == chat_id and new_event.sender_id == user_id:
            await new_event.reply(f"تم استلام ردك: {new_event.text}")
            client.remove_event_handler(wait_reply, events.NewMessage)

    client.add_event_handler(wait_reply, events.NewMessage)
    x = await event.reply("ارسل ردك الآن...")
    if x.text == "/ابدأ":
        return
