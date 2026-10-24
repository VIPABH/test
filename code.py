from ABH import ABH
from telethon import  events
import asyncio
_emoji = [
    "🤣", "❤️", "👍", "👎", "🔥", "🥰", "👏", "😁", "🤯", "😱", "🤬", "😡", "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊",
    "🤡", "🥱", "☺️", "😍", "🐳", "❤️‍🔥", "🌚", "🌭", "😙", "💯", "⚡️", "🍌", "🏆", "😡", "😘", "🙊", "😎", "👾", "🤷‍♂️",
    "🤷‍♀️", "🤷", "☃️", "🗿", "🆒", "💘", "🙈", "😇", "😨", "🤝", "✍️", "🤗", "🫡", "🎅", "🎄", "😴", "😭", "🤓", "👻",
    "👨‍💻", "👀", "🎃", "🙈", "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈"]
async def react(event, chat=None, id=None, emojis=None):
    chat_id = chat if chat else event.chat_id
    msg_id = id if id else event.message.id
    status = [0, 0]    
    try:
        peer = await ABH.get_entity(chat_id)
        try:
            await ABH(GetMessagesViewsRequest(
                peer=peer,
                id=[int(msg_id)],
                increment=True
            ))
        except Exception:
            pass            
        emoji =emojis
        await ABH(SendReactionRequest(
            peer=peer,
            msg_id=int(msg_id),
            reaction=[ReactionEmoji(emoticon=emoji)],
            big=False
        ))
        status[0] += 1
    except Exception as er:
        await event.reply(f'{er} ----- {emoji}')
        status[1] += 1
    await asyncio.sleep(1)
@ABH.on(events.NewMessage)
async def _(e):
    for em in _emoji:
        await react(e, emojis=em)
        await asyncio.sleep(1)
