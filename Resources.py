from telethon import events
async def ment(sender):
    name = getattr(sender, 'first_name', 'name')
    user_id = getattr(sender, 'id', None)
    if user_id is None:
        return "Unknown User"
    return f"[{name}](tg://user?id={user_id})"
async def mention(event):
    sender = await event.get_sender()
    return await ment(sender)
