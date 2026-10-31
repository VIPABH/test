from telethon.tl.functions.channels import InviteToChannelRequest
from ABH import *
@ABH.on(events.NewMessage)
async def _(e):
    await add_bot_to_channel(e.chat_id, '@fristagent')
async def add_bot_to_channel(chat_id, bot_username):
    try:
        bot_entity = await ABH.get_entity(bot_username)
        await ABH(InviteToChannelRequest(
            channel=int(chat_id),
            users=[bot_entity]
        ))
        
        print(f"تمت إضافة البوت {bot_username} إلى القناة بنجاح!")
        return True
    except Exception as e:
        print(f"فشل إضافة البوت: {e}")
        return False
