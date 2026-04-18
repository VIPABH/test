from ABH import *
x = []
@ABH.on(events.NewMessage)
async def handler(e):
    id = e.sender_id
    if id not in x:
        x.append(id)
        await e.reply("Hello")
    if len(x) == 10:
        y = await ABH.get_entity(x)
        await e.reply(y)
