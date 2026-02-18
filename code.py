from ABH import *
b = [
    Button.inline("اضف قناة", data="add"),
    Button.inline("حذف قناة", data="del"),
    Button.inline("عرض القنوات", data="get"),
@ABH.on(events.NewMessage(pattern="^/start"))
async def start(e):
    if not e.is_private:
        return
