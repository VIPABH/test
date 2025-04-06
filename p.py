from telethon import TelegramClient, events
import os

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

ABH = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.NewMessage(pattern='/check'))
async def check_admin_status(event):
    try:
        perms = await ABH.get_permissions(event.chat_id, event.sender_id)

        if perms.is_creator:
            await event.reply("👑 أنت المالك (Creator).")
        elif perms.is_admin:
            await event.reply("🛡️ أنت مشرف (Admin).")
        else:
            await event.reply("👤 أنت عضو عادي.")
    except Exception as e:
        await event.reply(f"⚠️ لم أتمكن من التحقق.\nالسبب: {str(e)}")

ABH.run_until_disconnected()
