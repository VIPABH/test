from Resources import *
from ABH import *
session = {}
@ABH.on(events.NewMessage(pattern=r'^اهمس (.*)'))
async def whisper_list_handler(e):
    input_data = e.pattern_match.group(1).strip()
    await e.reply(input_data)
