from Resources import *
from ABH import *
import uuid
import re

whisper_session = {}


@ABH.on(events.NewMessage(pattern=r'^(اهمس|همس[هة])(?:\s+(.+))?$'))
async def whisper(e):

    id = e.sender_id

    anymous = await bot()

    users = []
    targets = e.pattern_match.group(2)

    if not targets:
        return await react(e, '😁')

    async def custom_user(user):

        user = user.strip()

        if not user:
            return

        # ID
        if user.isdigit():
            users.append(int(user))

        # Username
        elif user.startswith('@') and len(user) > 1:
            try:
                full_user = await ABH.get_entity(user)
                users.append(full_user.id)
            except ValueError:
                return

    # استخراج اليوزرات والـ IDs
    for user in re.findall(r'@\w+|\d+', targets):
        await custom_user(user)

    if not users:
        return await e.reply(
            "ما لكيت مستخدم صالح."
        )

    owner_name = await mention(e)

    whisper_id = str(uuid.uuid4())[:6]

    whisper_session[id] = {
        'owmer': e.sender_id,
        'owner_name': owner_name,
        'to': users,
        'to_name': [
            await ment(user)
            for user in users
        ],
        'whisper_id': whisper_id,
    }

    url = f"https://t.me/{anymous.username}?start={whisper_id}"

    start_button = Button.url(
        'اضغط هنا للبدء',
        url=url
    )

    del_button = Button.inline(
        "حذف الهمسة",
        data=f'del_l:{id}'
    )

    to_names = ' و '.join(
        whisper_session[id]['to_name']
    )

    text = (
        f'همسة جارية الانشاء من '
        f'( {owner_name} ) إلى '
        f'( {to_names} ) 🙂🙂'
    )

    await e.reply(
        text,
        buttons=[
            [start_button],
            [del_button]
        ]
    )
