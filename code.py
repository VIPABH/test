from ABH import *
from Resources import *
target_bot_id = 2080276323
yt_session = {}
@ABH.on(events.NewMessage(pattern='^(حمل|يوت|تحميل|yt) ?(.*)', incoming=True))
async def yt_func(e):
    # if not e.is_group:return
    if e.sender_id ==  7278066500:return
    cmd = e.pattern_match.group(1)
    # if cmd != 'حمل':
    #     l = lock(e, 'يوت')
    #     if not l:return
    query = e.pattern_match.group(2)
    if not query:
        r = await e.get_reply_message()
        if not r:return await e.reply('اهلا عزيزي شنو تحب احملك؟')
        query = r.text
    await user.send_message(-1002219196756, 'يوت '+query)
    yt_session[e.id] = {
        'query': query
    }
@ABH.on(events.MessageEdited(from_users=target_bot_id))
async def resend_edited_media(event):
    msg = event.message
    if not msg.media:
        return
    await ABH.send_file(
        event.chat_id,
        file=msg.media,
    )
