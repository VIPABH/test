# from telethon import TelegramClient, events
# import os
# ttl_seconds = 10  # مدة التدمير الذاتي
# api_id = int(os.environ.get('API_ID'))
# api_hash = os.environ.get('API_HASH')

# user = TelegramClient('user', api_id, api_hash)

# @user.on(events.NewMessage)
# async def s(e):
#     await user.send_file(
#         e.chat_id,
#         file='موارد/photo_2025-02-10_11-40-17.jpg',
#         supports_streaming=False,      # لأننا نرسل صورة وليس فيديو
#         protected_content=True,        # حماية الصورة من التحميل وإعادة التوجيه
#         ttl_seconds=ttl_seconds        # تفعيل التدمير الذاتي
#     )

# user.start()
# user.run_until_disconnected()
