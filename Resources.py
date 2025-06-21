from telethon import events
async def ment(sender):
        name = sender.first_name or 'name'
        id = sender.id
        return f"[{name}](tg://user?id={id})"
async def mention(event):
        name = event.first_name or 'name'
        id = event.id
        return f"[{name}](tg://user?id={id})"
