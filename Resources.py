from telethon import events
async def mention(event):
    name = getattr(event.sender, 'first_name', None) or 'غير معروف'
    user_id = event.sender_id
    return f"[{name}](tg://user?id={user_id})"
async def ment(sender):
    name = sender.first_name
    user_id = sender.id
    return f"[{name}](tg://user?id={user_id})"
async def hint(e):
    await ABH.send_message(wfffp, str(e))
