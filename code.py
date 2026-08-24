from telethon.tl.types import DocumentAttributeVideo
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
    # url = f"https://t.me/{anymous.username}?start={whisper_id}"
    # start_button = Button.url('اضغط هنا للبدء', url=url, style=green, icon=5258073068852485953)
    start_button = Button.url("فتح الهمسة", url=f"https://t.me/{(await ABH.get_me()).username}?start={whisper_id}")
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
        'owner_id': e.sender_id, 
        'to': users,
        'to_name': to_names,
        'whisper_id': whisper_id,
        'link': row_link(e),
        'chat_id': e.chat_id,
        'msg': msg.id,}
@ABH.on(events.NewMessage(pattern=r'/start (\w+)'))
async def start_with_param(e):
    whisper_id = e.pattern_match.group(1)
    id = e.sender_id
    if whisper_id in whisper_links:
        _type = whisper_links[whisper_id]['type']
        if _type == 'text':
            text = whisper_links[whisper_id]['text']
            return await e.reply(text)
        else:
            files = whisper_links[whisper_id]['file']
            texts = whisper_links[whisper_id]['text']
            ttls = whisper_links[whisper_id]['video_duration']
            grouped = list(zip(files, texts, ttls))
            for row_file, text, video_duration in grouped:
                file = await get_input_media(row_file)                
                await ABH.send_file(e.chat_id, file=file, caption=text, reply_to=e.id, ttl=int(video_duration))
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
async def forward_whisper(e):
    if not e.is_private:return
    if e.text.startswith("اهمس") or e.text.startswith("/start"):return
    sender_id = e.sender_id
    if sender_id not in whisper_session:return
    session = whisper_session[sender_id]
    whisper_id = session['whisper_id']
    whisper_links.setdefault(whisper_id, {
        'type': '',
        'text': [],
        'video_duration': [],
        'file': [],
        'full_info': whisper_session[sender_id],
    })
    if not whisper_id:return
    b = Button.url("فتح الهمسة", url=f"https://t.me/{(await ABH.get_me()).username}?start={whisper_id}")
    msg = e.message
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
        whisper_links[whisper_id]['type'] = 'media'
        whisper_links[whisper_id]['text'].append(e.text)
        whisper_links[whisper_id]['video_duration'].append(video_duration)
        whisper_links[whisper_id]['file'].append(await extract_media_data(e))
        t = "تم إرسال همسة ميديا بنجاح."
    else:
        whisper_links[whisper_id]['type'] = 'text'
        whisper_links[whisper_id]['text'] = msg.text
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
        buttons=[b])
    await e.reply(t)
    await ABH.send_message(whisper_session[sender_id]['chat_id'], f'هَمستك عزيزي (  {whisper_session[sender_id]["to_name"]} )', reply_to=msg.id)
    whisper_session.pop(id, None)
@ABH.on(events.CallbackQuery(pattern=b'^del_l:(\\d+)$'))
async def delete_whisper_callback(e):
    data = e.data
    id = int(e.pattern_match.group(1))
    sender_id = e.sender_id
    if id != sender_id:
        return await e.answer('🙄')
    whisper_session.pop(id, None)
    await e.edit(
        'تم حذف جلسة الهمسة',
        buttons=Button.url("كيف اهمس", url=f"https://t.me/{(await bot()).username}?start=how_can_i_whisper", style=red))
