from telethon import events
async def mention(event, sender):
        name = sender.first_name or 'name'
        id = sender.id
        return f"[{name}](tg://user?id={id})"
