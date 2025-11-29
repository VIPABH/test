from telethon import TelegramClient, events

ttl_seconds = 10

user = TelegramClient('user', api_id, api_hash)

@user.on(events.NewMessage(outgoing=True))
async def s(e):
    await user.send_file(
        e.chat_id,
        file='موارد/photo_2025-02-10_11-40-17.jpg',
        supports_streaming=True,
        ttl_seconds=ttl_seconds
    )

user.start()
user.run_until_disconnected()
