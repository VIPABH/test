from ABH import *
@ABH.on(events.NewMessage)
async def x(e):
    await e.reply(f"~~{e.text}~~/n")
