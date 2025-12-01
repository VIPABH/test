from ABH import ABH
@ABH.on(events.NewMessage)
async def start(e):
    print(e)
