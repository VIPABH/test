from telethon.tl.functions.channels import GetFullChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import UpdateChannelParticipant
from telethon import events
from Resources import *
from ABH import ABH
import asyncio
@ABH.on(events.Raw)
async def get_invite_link(e):
    chat_id = getattr(event, "channel_id", None)
    link = await ABH(ExportChatInviteRequest(chat_id))
    print("رابط الدعوة:", link.link)
