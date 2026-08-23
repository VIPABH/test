from Resources import *
from ABH import *
import uuid, re
whisper_session = {}
message = {}
@ABH.on(events.NewMessage(pattern=r'^(اهمس|همس[هة])(?:\s+(.+))?$'))
async def whisper(e):
    id = e.sender_id
    anymous = await bot()
    users = set()
    targets = e.pattern_match.group(2)
    if not targets:
        return await react(e, '😁')
    if id in whisper_session:
        session = whisper_session[id]
        text = f'عذرا ماتكدر تسوي همسة \n عندك جلسة بعدك ما مكملها'
        del_button = [
            Button.inline("حذف الهمسة", data=f'del_l:{id}', style=red, icon=5258130763148172425),
            Button.url("أكمال الهمسة", url=f"https://t.me/{anymous.username}?start={session['whisper_id']}", style=green, icon=5258073068852485953),
            Button.url("رابط الهمسة", url=session['link'], style=blue, icon=5258262708838472996),
        ]
        button = chunk_list(del_button, 2)
        return await e.reply(text, buttons=button)
    async def custom_user(user):
        user = user.strip()
        if not user: return
        try:
            full_user = await ABH.get_entity(user)
            if not getattr(full_user, "bot", False):
                users.add(full_user.id)
        except ValueError:
            return
    for user in re.findall(r'@\w+|\d+', targets):
        await custom_user(user)
    users = list(users)
    if not users: return await e.reply("ما لكيت المستخدم.")
    owner_name = await mention(e)
    whisper_id = str(uuid.uuid4())[:6]
    url = f"https://t.me/{anymous.username}?start={whisper_id}"
    start_button = Button.url('اضغط هنا للبدء', url=url, style=green, icon=5258073068852485953)
    _mentions = [await ment(user) for user in users]
    to_names = ' و '.join(_mentions)
    text = (
        f'همسة جارية الانشاء من '
        f'( {owner_name} ) إلى '
        f'( {to_names} ) 🙂🙂')
    msg = await PROFILE_SEND(e, text, buttons=[start_button])
    whisper_session[id] = {
        'to': users,
        'to_name': _mentions,
        'whisper_id': whisper_id,
        'link': row_link(e),
        'msg': msg.id,}
    await e.reply(list(map(int, whisper_session.keys())))
@ABH.on(events.NewMessage(pattern=r'/start (\w+)'))
async def start_with_param(e):
    whisper_id = e.pattern_match.group(1)
    id = e.sender_id
    if not (id in whisper_session):
        return await chs(e, 'عزيزي انت اصلا ما عندك جلسة اهمس')
    session = whisper_session[id]
    await chs(e, 'ارسل الان همسة ميديا او نص')
    del session
@ABH.on(events.NewMessage(incoming=True))
async def recive_whisper(e):
    id = e.sender_id
    if id not in whisper_session: return     
    if not e.is_private: return
    if e.text and e.text.startswith('/start'): return
    if e.text == 'دز':
        await e.reply(str(message[id]))
        return
    msg = e.message 
    if msg.media:
        if e.grouped_id:
            if id not in message:
                message[id] = {'media': [], 'type': 'media'}
                await chs(e, 'تم ارسال الهمسة ب نجاح')
            message[id]['media'].append(await extract_media_data(e))
        else:
            message[id] = {'media': [], 'type': 'media'}
            message[id]['media'].append(await extract_media_data(e))
    else:
        message[id] = {'type': 'text', 'text': e.text}
@ABH.on(events.CallbackQuery(pattern=b'^del_l:(\\d+)$'))
async def delete_whisper_callback(e):
    data = e.data
    id = int(e.pattern_match.group(1))
    sender_id = e.sender_id
    if id != sender_id:
        return await e.answer('🙄')
    await e.edit('تم حذف جلسة الهمسة', buttons=Button.url("كيف اهمس", url=f"https://t.me/{(await bot()).username}?start=how_can_i_whisper"))
