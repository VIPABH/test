from telethon.tl.types import DocumentAttributeVideo
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
        text = 'عذرا ماتكدر تسوي همسة \n عندك جلسة بعدك ما مكملها'
        del_button = [
            Button.inline("حذف الهمسة", data=f'del_l:{id}', style=red, icon=5258130763148172425),
            Button.url("أكمال الهمسة", url=f"https://t.me/{anymous.username}?start={session['whisper_id']}", style=green, icon=5258073068852485953),
            Button.url("رابط الهمسة", url=session['link'], style=blue, icon=5258262708838472996),
        ]
        button = chunk_list(del_button, 2)
        return await e.reply(text, buttons=button)
    async def custom_user(user):
        user = user.strip()
        if not user:
            return
        try:
            full_user = await ABH.get_entity(user)
            if not getattr(full_user, "bot", False):
                users.add(full_user.id)
        except Exception:
            return
    for user in re.findall(r'@\w+|\d+', targets):
        await custom_user(user)
    users.discard(id)
    users = list(users)
    if not users:
        return await e.reply("ما لكيت المستخدم.")
    owner_name = await mention(e)
    whisper_id = str(uuid.uuid4())[:6]
    url = f"https://t.me/{anymous.username}?start={whisper_id}"
    start_button = Button.url('اضغط هنا للبدء', url=url, style=green, icon=5258073068852485953)
    _mentions = [await ment(user) for user in users]
    count = len(_mentions)
    to_names = ' و '.join(_mentions)
    text = (
        f'همسة جارية الانشاء من '
        f'( {owner_name} ) إلى '
        f'( {to_names} ) 🙂🙂')
    msg = await PROFILE_SEND(e, text, buttons=[start_button])
    whisper_session[id] = {
        'owner': await mention(e),
        'to': users,
        'to_name': to_names,
        'count': count,
        'whisper_id': whisper_id,
        'link': row_link(e),
        'chat_id': e.chat_id,
        'msg': msg.id,}
@ABH.on(events.NewMessage(pattern=r'/start (\w+)'))
async def start_with_param(e):
    whisper_id = e.pattern_match.group(1)
    id = e.sender_id
    if whisper_id in whisper_links:
        return await e.reply(str(whisper_links(whisper_id)))
    if id not in whisper_session:
        return await chs(e, 'عزيزي انت اصلا ما عندك جلسة اهمس')
    session = whisper_session[id]
    if session['whisper_id'] != whisper_id:
        return await chs(e, 'هذا الرابط غير صالح لجلستك الحالية')
    await chs(e, 'ارسل الان همسة ميديا او نص')
processed_groups = set()
whisper_links = {}
# @ABH.on(events.NewMessage(incoming=True, from_users=list(map(int, whisper_session.keys()))))
@ABH.on(events.NewMessage(incoming=True))
async def forward_whisper(event):
    if not event.is_private:return
    if event.text.startswith("اهمس") or event.text.startswith("/start"):return
    sender_id = event.sender_id
    if sender_id not in whisper_session:return
    session = whisper_session[sender_id]
    whisper_id = session['whisper_id']
    whisper_links.setdefault(whisper_id, {})
    if not whisper_id:return
    b = Button.url("فتح الهمسة", url=f"https://t.me/{(await ABH.get_me()).username}?start={whisper_id}")
    msg = event.message
    is_photo = getattr(msg.media, 'photo', None)
    is_video = False
    video_duration = None
    if getattr(msg, "voice", None) or (msg.document and msg.document.mime_type == "audio/ogg"):
        video_duration = None
    if msg.media and (is_photo or getattr(msg.media, 'document', None) or getattr(msg, "voice", None)):
        if is_photo:
            video_duration = 30
        elif getattr(msg.media, 'document', None):
            for attr in msg.media.document.attributes:
                if isinstance(attr, DocumentAttributeVideo):
                    video_duration = attr.duration
                    is_video = True
                    break
            if not is_video and not (msg.document and msg.document.mime_type == "audio/ogg"):
                return
        whisper_links[whisper_id]['video_duration'] = video_duration
        whisper_links[whisper_id].setdefault('original_msg_id', [])
        whisper_links[whisper_id]['original_msg_id'].append(msg.id)
        whisper_links[whisper_id]['from_user_chat_id'] = sender_id
        if not ('done' in whisper_links[whisper_id]):
            whisper_links[whisper_id]['done'] = True
        t = "تم إرسال همسة ميديا بنجاح."
    elif msg.text:
        whisper_links[whisper_id]['text'] = msg.text
        if not ('done' in whisper_links[whisper_id]):
            whisper_links[whisper_id]['done'] = True
        t = "تم إرسال همسة بنجاح."
    gid = getattr(msg, 'grouped_id', None)
    if msg.media and gid:
        if gid in processed_groups:
            return
        processed_groups.add(gid)
    msg = await ABH.edit_message(
        whisper_session[sender_id]['chat_id'],
        whisper_session[sender_id]['msg'], 
        text=f'همسة مرسلة من ({whisper_session[sender_id]["to_name"]} ) إلى ( {whisper_session[sender_id]["to_name"]} ) 🙂🙂',
        buttons=[b]
    )
    await event.reply(str(t))
    await ABH.send_message(data['chat_id'], f'{'هَمستك' if whisper_session[sender_id]['count '] > 1 else 'همستكم'} عزيزي (  {whisper_session[sender_id]["to_name"]} )', reply_to=msg.id)
@ABH.on(events.CallbackQuery(pattern=b'^del_l:(\\d+)$'))
async def delete_whisper_callback(e):
    data = e.data
    id = int(e.pattern_match.group(1))
    sender_id = e.sender_id
    if id != sender_id:
        return await e.answer('🙄')
    whisper_session.pop(id, None)
    message.pop(id, None)
    await e.edit(
        'تم حذف جلسة الهمسة',
        buttons=Button.url("كيف اهمس", url=f"https://t.me/{(await bot()).username}?start=how_can_i_whisper", style=red))
