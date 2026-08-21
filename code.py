from Resources import *
from ABH import *
import uuid
whisper_session = {}
@ABH.on(events.NewMessage(pattern=r'^(اهمس|همس[هة])(?:\s+(.+))?$'))
async def whisper(e):
    # if not lock(e, 'همسة'):
    #     return await e.reply('اوامر الهمسة معطلة💔')
    id = e.sender_id
    # if id in whisper_session:
    target = await to(e)
    target_id = getattr(target, "sender_id", None) or getattr(target, "id", None)
    if not target:return await e.reply("حاول تشغل الامر اما بالرد او باليوزر او المنشن")
    if getattr(target, "bot", False):
        return 
    if target_id == id:
        return await e.reply("شني خالي تسوي همسه لنفسك")
    anymous = await bot()
    if target_id == anymous.id:
        return await e.reply("تسويلي همسه 😁؟")
    users = []
    targets = e.pattern_match.group(2)
    if not targets:return await react(e, '😁')
    async def custom_user(user):
        if user.isdigit():
            users.append(user)
        elif user.startswith('@'):
            full_user = await ABH.get_entity(user)
            users.append(full_user.id)
    if len(target) > 1:
        for user in targets:
            custom_user(user)
    else:
        custom_user(users)
    owner_name = await mention(e)
    whisper_id = str(uuid.uuid4())[:6]
    whisper_session.setdefault(id, {})
    whisper_session[id] = {
        'owmer': e.sender_id,
        'owner_name': owner_name,
        'to': users,
        'to_name': [await ment(user) for user in users],
        'whisper_id': str(uuid.uuid4())[:6],
        }
    url = f"https://t.me/{anymous.username}?start={whisper_id}"
    start_button = Button.url('اضغط هنا للبدء', url=url, style=blue)
    del_button = Button.inline("حذف الهمسة", data=f'del_l:{id}', style=red)
    text = f'همسة جارية الانشاء من ( {await mention(e)} ) إلى ( {'و'.join(whisper_session[id]['to_name'])} ) 🙂🙂'
    await e.reply(text, button=[start_button])
