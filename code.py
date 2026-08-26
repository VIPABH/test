from telethon.tl.types import DocumentAttributeVideo
from telethon.errors import TtlMediaInvalidError
from Resources import *
from Program import chs
from ABH import *
import uuid, re
messages = {}
@ABH.on(events.NewMessage(pattern=r'^اهمس(?:\s+(.+))?$', from_users=[wfffp]))
async def whisper(e):
    id = e.sender_id    
    if id in whisper_session:
        session = whisper_session[id]
        text = 'عذرا ماتكدر تسوي همسة \n عندك جلسة بعدك ما مكملها'
        del_button = [
            Button.inline("حذف الهمسة", data=f'del_l:{id}', style=red, icon=5258130763148172425),
            Button.url("أكمال الهمسة", url=f"https://t.me/{anymous.username}?start={session['whisper_id']}", style=green, icon=5258073068852485953),
            Button.url("رابط الهمسة", url=session['link'], style=blue, icon=5258262708838472996),]
        button = chunk_list(del_button, 2)
        return await e.reply(text, buttons=button)
    text = e.text
    List = text.split()
    del List[0]
    row_users = set()
    for user in List:
        if user.startswith('@') or user.lstrip('-').isdigit():
            val = int(user) if user.lstrip('-').isdigit() else user
            row_users.add(val)
    row_users.discard(id)
    if not row_users:
        if not e.is_reply:
            return await e.reply("ما لكيت المستخدم.")
        r = await e.get_reply_message()
        row_users.add(r.sender_id)
    users = []
    full_users = await ABH.get_entity(list(row_users))
    if not isinstance(full_users, list):
        full_users = [full_users]
    for user in full_users:
        if user and not getattr(user, 'bot', False):
            users.append(user)
    if not users:return await e.reply("ما لكيت مستخدم صالح.")
    anymous = await bot() 
    whisper_id = "nr"+str(uuid.uuid4())[:6]
    print(whisper_id)
    url = f"https://t.me/{anymous.username}?start={whisper_id}"
    start_button = Button.url('اضغط هنا للبدء', url=url, style=green, icon=5258073068852485953)
    owner_name = await mention(e)
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
        'owner': e.sender_id, 
        'owner_name': owner_name, 
        'to': users,
        'whisper_id': whisper_id,
        'to_name': to_names,
        'link': row_link(e),
        'chat_id': e.chat_id,
        'msg': msg.id,
        }
    messages.setdefault(whisper_id, {
        'type': None,
        'text': [],
        'video_duration': [],
        'file': [],
        'owner': e.sender_id, 
        'to': users,
        'seen': set(),
        'chat_id': e.chat_id,
        'msg': msg.id,
        })
whispers_file = 'whispers.json'
if os.path.exists(whispers_file):
    try:
        with open(whispers_file, 'r', encoding='utf-8') as f:
            whisper_session = json.load(f)
    except json.JSONDecodeError:
        whisper_session = {}
else:
    whisper_session = {}
def save_whispers():
    with open(whispers_file, 'w', encoding='utf-8') as f:
        json.dump(whisper_session, f, ensure_ascii=False, indent=2)
async def _start_with_param(e):
    whisper_id = e.pattern_match.group(1)
    data = whisper_session.get(whisper_id)
    if not data:
        return
    sender_id = e.sender_id
    if sender_id not in (data['from'], data['to']):
        await e.reply("لا يمكنك مشاهدة هذه الهمسة.")
        return
    if sender_id == data['to']:
        fb = [
            Button.inline(
                'حذف الهمسة',
                data=f"del_l:{data['from']}"),
            Button.url(
                "رؤية الهمسة",
                url=f"https://t.me/{(await ABH.get_me()).username}?start={whisper_id}")]
        try:
            await ABH.edit_message(
                data['chat_id'],
                data['editmsg_id'],
                text=(
                    f"همسة مرسلة من ({data['sender_mention']}) "
                    f"إلى ({data['reciver_mention']}) 🙂"
                ),
                buttons=fb
            )
        except Exception:
            pass
    if 'original_msg_id' in data and 'from_user_chat_id' in data:
        originals = await ABH.get_messages(
            data['from_user_chat_id'],
            ids=data['original_msg_id'])
        for original in originals:
            if original.media:
                video_duration = data.get('video_duration')
                try:
                    await ABH.send_file(
                        sender_id,
                        file=original,
                        caption=original.message or None,
                        reply_to=e.id,
                        ttl=int(video_duration) if video_duration else None)
                except Exception:
                    await ABH.send_file(
                        sender_id,
                        file=original,
                        caption=original.message or None,
                        reply_to=e.id)
            elif original.text:
                await ABH.send_message(sender_id, original.text)
    elif 'text' in data:
        await e.reply(data['text'])
@ABH.on(events.NewMessage(pattern=r'/start (\w+)'))
async def start_with_param(e):
    whisper_id = e.pattern_match.group(1)
    if not whisper_id.startswith('nr'):return await _start_with_param(e)
    id = e.sender_id
    whisper = messages[whisper_id]
    if not (id in whisper['to']) and id != whisper['owner']:
        return await chs(e, 'عذرا بس ماتكدر تشوف الهمسة لانها مو موجهه الك.')
    if id in whisper['to'] and whisper['type'] is None:return await chs(e, 'همستك جارية الانشاء عزيزي')
    _type = messages[whisper_id]['type']
    seen = messages[whisper_id]['seen']
    opened = False
    anymous = await bot() 
    url = f"https://t.me/{anymous.username}?start={whisper_id}"
    start_button = Button.url('اضغط هنا للبدء', url=url, style=green, icon=5258073068852485953)
    if _type == 'text':
        text = messages[whisper_id]['text']
        if not (id in seen):
            seen.add(id)
            opened = True
        return await e.reply(text)
    elif _type == 'media':
        text = messages[whisper_id]['text']
        if not (id in seen):
            seen.add(id)
            opened = True
        files = messages[whisper_id]['file']
        texts = messages[whisper_id]['text']
        ttls = messages[whisper_id]['video_duration']
        grouped = list(zip(files, texts, ttls))
        for row_file, text, video_duration in grouped:
            file = await get_input_media(row_file)
            try:
                return await ABH.send_file(e.chat_id, file=file, caption=text, reply_to=e.id, ttl=int(video_duration))
            except TtlMediaInvalidError:
                return await ABH.send_file(e.chat_id, file=file, caption=text, reply_to=e.id)
    else:await chs(e, 'ارسل الان همسة ميديا او نص')
    if opened:
        who_open = [await ment(user) for user in seen]
        users = ' و '.join(who_open)
        text = f'همسة مرسلة من ({whisper_session[sender_id]["to_name"]} ) إلى ( {whisper_session[sender_id]["to_name"]} ) 🙂🙂',
        buttons = [Button.url('فتح الهمسة', url=url, style=blue), Button.inline('حذف الهمسة', data=f'del_l:{whisper['owner']}', style=red)]
        await ABH.edit_message(whisper['chat_id'], f'~~{text}~~\n تمت رؤية الهمسة من قبل ( {users} )', buttons=buttons)
processed_groups = set()
@ABH.on(events.NewMessage(incoming=True))
async def recive_whisper(e):
    if not e.is_private:return
    if e.text.startswith("اهمس") or e.text.startswith("/start"):return
    sender_id = e.sender_id
    if sender_id not in whisper_session:return
    session = whisper_session[sender_id]
    whisper_id = session['whisper_id']
    if not whisper_id:return
    # url = f"https://t.me/{anymous.username}?start={whisper_id}"
    # start_button = Button.url('فتح الهمسة', url=url, style=green, icon=5258073068852485953)
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
        messages[whisper_id]['type'] = 'media'
        messages[whisper_id]['text'].append(e.text)
        messages[whisper_id]['video_duration'].append(video_duration)
        messages[whisper_id]['file'].append(await extract_media_data(e))
        t = "تم إرسال همسة ميديا بنجاح."
    else:
        messages[whisper_id]['type'] = 'text'
        messages[whisper_id]['text'] = msg.text
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
    del whisper_session[sender_id]
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
        buttons=Button.url("كيف اهمس", url=f"https://t.me/{(await bot()).username}?start=how_can_i_whisper", style=blue))
