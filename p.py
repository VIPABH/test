from telethon.sync import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError, ChannelInvalidError, ChannelPrivateError, ChatAdminRequiredError, RPCError

import os
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# إعدادات البوت


client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# معرف القناة
channel_username = 'x04ou'  # بدون @

@client.on(events.NewMessage(pattern='/start'))
async def handler(event):
    user_id = event.sender_id

    try:
        # التحقق من الاشتراك
        await client(GetParticipantRequest(channel_username, user_id))
        await event.respond("✅ مرحبًا بك، تم التحقق من اشتراكك ويمكنك الآن استخدام البوت.")
    
    except UserNotParticipantError:
        # المستخدم غير مشترك
        await event.respond(
            f"🚫 يجب الاشتراك أولًا في القناة لاستخدام البوت:\n"
            f"📢 https://t.me/{channel_username}\n"
            f"ثم أعد إرسال /start"
        )

    except (ChannelPrivateError, ChannelInvalidError):
        await event.respond("⚠️ لا يمكن التحقق من القناة. تأكد أن القناة عامة وأن البوت عضو فيها.")
    
    except ChatAdminRequiredError:
        await event.respond("⚠️ يحتاج البوت لصلاحيات أعلى للوصول إلى القناة.")
    
    except RpcError as e:
        await event.respond("⚠️ خطأ في الاتصال بخوادم تيليجرام. حاول لاحقًا.")
        print(f"RPC Error: {e}")
    
    except Exception as e:
        await event.respond("❌ حدث خطأ غير متوقع. تم تسجيله للتحقيق.")
        print(f"Unhandled exception: {e}")

client.run_until_disconnected()
