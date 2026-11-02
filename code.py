import re
import random
from telethon import events
from telethon.tl.functions.messages import SendReactionRequest, GetMessagesViewsRequest
from telethon.tl.types import ReactionEmoji, PeerChannel
from ABH import ABH, ABHS

# الروابط المدعومة: https://t.me/c/123456789/10 أو https://t.me/username/10
LINK_PATTERN = r"(?:https?://)?t\.me/(?:c/)?([^/]+)/(\d+)"

@ABH.on(events.NewMessage(pattern=r"^/react\s+(.+)"))
async def react_via_link(event):
    link = event.pattern_match.group(1).strip()
    match = re.search(LINK_PATTERN, link)
    
    if not match:
        await event.reply("❌ رابط المنشور غير صحيح.")
        return
    
    channel_identifier, msg_id = match.groups()
    msg_id = int(msg_id)
    
    # تحديد الـ peer حسب نوع القناة (عامة عبر يوزرنيم أو خاصة عبر أيدي)
    if channel_identifier.isdigit():
        peer = PeerChannel(int(channel_identifier))
    else:
        peer = channel_identifier
        
    emojis_list = ['❤️', '🕊', '🌚', '🔥', '👍']
    success_count = 0

    for client in ABHS:
        try:
            # 1. زيادة المشاهدة
            await client(GetMessagesViewsRequest(
                peer=peer,
                id=[msg_id],
                increment=True
            ))
            
            # 2. إرسال التفاعل
            emoji = random.choice(emojis_list)
            await client(SendReactionRequest(
                peer=peer,
                msg_id=msg_id,
                reaction=[ReactionEmoji(emoticon=emoji)],
                big=False
            ))
            
            success_count += 1
        except Exception:
            continue

    await event.reply(f"✅ تم تنفيذ التفاعل والمشاهدات بنجاح بواسطة {success_count} حساب.")
