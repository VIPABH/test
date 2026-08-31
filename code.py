from telethon import events
from telethon.tl.types import (
    ReplyInlineMarkup,
    KeyboardButtonRow,
    InputKeyboardButtonUserProfile,
    InputUser,
)
from ABH import ABH
@ABH.on(events.NewMessage(pattern=r'\.زر'))
async def button_mention(e, id=None, text=None):
    # if not id:return
    input_peer = await ABH.get_input_entity(e.sender_id)
    button_text = text if text else getattr(user_entity, 'first_name', 'User')    
    user_input = InputUser(user_id=input_peer.user_id, access_hash=input_peer.access_hash)    
    markup = ReplyInlineMarkup(
        rows=[
            KeyboardButtonRow(
                buttons=[
                    InputKeyboardButtonUserProfile(
                        text=button_text,
                        user_id=user_input
                    )
                ]
            )
        ]
    )
    await e.reply('[]', buttons=markup)
    return markup
