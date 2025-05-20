from telethon import TelegramClient, events
import os

SESSION='session'
API_ID=int(os.getenv("API_ID"))
API_HASH=os.getenv("API_HASH")
BOT_TOKEN=os.getenv("BOT_TOKEN")

ABH=TelegramClient(SESSION,API_ID,API_HASH).start(bot_token=BOT_TOKEN)

@ABH.on(events.NewMessage(pattern="^يوزراتي$"))
async def handler(event):
 s=await event.get_sender()
 usernames=[x.username for x in s.usernames] if getattr(s,"usernames",None) else []
 if s.username: usernames.insert(0, s.username)
 usernames=list(dict.fromkeys(usernames))
 utext="\n".join(f"@{u}" for u in usernames)
 await event.reply(utext if usernames else "ليس لديك أي يوزرات NFT")

@ABH.on(events.NewMessage(pattern="^يوزراته$"))
async def handler(event):
 r=await event.get_reply_message()
 if not r:
  await event.reply("يجب الرد على رسالة المستخدم")
  return
 s=await r.get_sender()
 usernames=[x.username for x in s.usernames] if getattr(s,"usernames",None) else []
 if s.username: usernames.insert(0, s.username)
 usernames=list(dict.fromkeys(usernames))
 utext="\n".join(f"@{u}" for u in usernames)
 await event.reply(utext if usernames else "ليس لديه أي يوزرات NFT")
@ABH.on(events.NewMessage(pattern="^يوزري$"))
async def handler(event):
 s=await event.get_sender()
 u=s.username or (list(dict.fromkeys([x.username for x in s.usernames]))[0] if getattr(s,"usernames",None) else None)
 await event.reply(f"`@{u}` @{u}" if u else "ليس لديك يوزر")

@ABH.on(events.NewMessage(pattern="^يوزره|يوزرة|اليوزر$"))
async def handler(event):
 r=await event.get_reply_message()
 if not r:
  await event.reply("يجب الرد على رسالة المستخدم")
  return
 s=await r.get_sender()
 u=s.username or (list(dict.fromkeys([x.username for x in s.usernames]))[0] if getattr(s,"usernames",None) else None)
 await event.reply(f"`@{u}` @{u}" if u else "ليس لديه يوزر")

ABH.run_until_disconnected()
