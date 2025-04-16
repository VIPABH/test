from telethon import TelegramClient, events
import os, asyncio
import aiohttp #type: ignore
from datetime import datetime
from telethon.tl.types import ChannelParticipant, ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetParticipantRequest


api_id = int(os.getenv('API_ID', '123456'))
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
@ABH.on(events.NewMessage)
async def e(event):
    message_text = '>>>>'
    msg = await event.send_file(event.chat_id, photo='https://files.catbox.moe/k44qq6.mp4', caption=message_text)
    await asyncio.sleep(2)
    message_text = '...'
    await msg.edit(event.chat_id, caption=message_text)

ABH.run_until_disconnected()
