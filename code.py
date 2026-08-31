from telethon import events
from telethon.tl.types import (
    ReplyInlineMarkup,
    KeyboardButtonRow,
    InputKeyboardButtonUserProfile,
    InputUser,
)
from ABH import ABH

@ABH.on(events.NewMessage(pattern=r'\.زر'))
async def main(e):
    target_user_id = 1910015590
    button_text = 'ابـ،ـن،هـ.ـاشـ.ـم ✘'

    # لازم نجيب access_hash الخاص باليوزر عن طريق get_input_entity
    input_peer = await ABH.get_input_entity(target_user_id)
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

    await ABH.send_message(e.chat_id, 'نص الرسالة هنا', buttons=markup)
