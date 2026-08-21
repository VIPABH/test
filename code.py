from Resources import *
from ABH import *
import uuid, re
whisper_session = {}
@ABH.on(events.NewMessage(pattern=r'^(اهمس|همس[هة])(?:\s+(.+))?$'))
async def whisper(e):
    id = e.sender_id
    anymous = await bot()
    users = set()
    targets = e.pattern_match.group(2)
    if not targets:
        return await react(e, '😁')
    async def custom_user(user):
        user = user.strip()
        if not user:
            return
        if user.isdigit():
            users.add(int(user))
        elif user.startswith('@') and len(user) > 1:
            try:
                full_user = await ABH.get_entity(user)
                if not getattr(full_user, "bot", False):
                    users.add(full_user.id)
            except ValueError:
                return
    for user in re.findall(r'@\w+|\d+', targets):
        await custom_user(user)
    users = list(users)
    if not users:return await e.reply("ما لكيت المستخدم.")
    owner_name = await mention(e)
    whisper_id = str(uuid.uuid4())[:6]
    whisper_session[id] = {
        'owmer': e.sender_id,
        'owner_name': owner_name,
        'to': users,
        'to_name': [await ment(user) for user in users],
        'whisper_id': whisper_id,}
    url = f"https://t.me/{anymous.username}?start={whisper_id}"
    start_button = Button.url('اضغط هنا للبدء',url=url)
    del_button = Button.inline("حذف الهمسة",data=f'del_l:{id}')
    to_names = ' و '.join(whisper_session[id]['to_name'])
    text = (
        f'همسة جارية الانشاء من '
        f'( {owner_name} ) إلى '
        f'( {to_names} ) 🙂🙂')
    await e.reply(text, buttons=[start_button])
