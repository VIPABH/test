from telethon import events
from ABH import ABH
import os, json
def save(file, data):
    if not os.path.exists(file):
        os.mkdir(file)
    if not data or data is None:
        load = json.load(open(os.path.join(file)))
        return load
    with open(os.path.join(file), "w") as f:
        json.dump(data, f)
        load = json.load(open(os.path.join(file)))
        return load
@ABH.on(events.NewMessage(pattern=r"تخزين"))
async def handler(event):
    r = await event.get_reply_message()
    if r:
        data = r.text
        s = save('test.json', data)
        await event.reply("تم تخزين الرسالة.")
        await event.reply(s)
