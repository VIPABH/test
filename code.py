from ABH import *
from telethon import events
from telethon.tl.custom import Button
from telethon.tl import types

# تعريف دالة mention وإضافتها لكلاس Button
def mention_button(text, user):
    return types.InputKeyboardButtonUserProfile(text=text, user_id=user)

Button.mention = staticmethod(mention_button)


@ABH.on(events.NewMessage)
async def _(e):
    user_entity = await ABH.get_input_entity(e.sender_id)
    
    await e.reply('>', buttons=[
        [Button.mention('--', user_entity)]
    ])
