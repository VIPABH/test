from telethon import TelegramClient, events
from telethon.tl.types import (
    ReplyInlineMarkup,
    KeyboardButtonRow)
    

@ABH.on(events.NewMessage(pattern=r'\.زر'))
async def main(e):
    target_user_id = 1910015590
    button_text = 'ابـ،ـن،هـ.ـاشـ.ـم ✘'

    markup = ReplyInlineMarkup(
        rows=[
            KeyboardButtonRow(
                buttons=[
                    KeyboardButtonUserProfile(
                        text=button_text,
                        user_id=target_user_id
                    )
                ]
            )
        ]
    )

    await ABH.send_message(e.chat_id, 'نص الرسالة هنا', buttons=markup)

