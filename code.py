from telethon import events, Button
from Resources import mention
from ABH import ABH
from telethon import TelegramClient
from telethon.tl.types import (
    ReplyInlineMarkup,
    KeyboardButtonRow,
    KeyboardButtonUserProfile,
)


@ABH.on(events.NewMessage))
async def main(e):
    target_user_id = 1910015590   # آيدي المستخدم اللي تريد الزر يودي لبروفايله
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

    await ABH.send_message(
        e.chat_id,
        'نص الرسالة هنا',
        buttons=markup
    )

