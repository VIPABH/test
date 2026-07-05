from ABH import *
import asyncio, yt_dlp, json, os, time, urllib.request
from telethon.tl.types import DocumentAttributeAudio, InputDocument
from concurrent.futures import ThreadPoolExecutor
from Resources import *
from telethon.tl.types import KeyboardButtonUserProfile, ReplyKeyboardMarkup, KeyboardButtonRow, KeyboardButton
@ABH.on(events.NewMessage(pattern=r".?ازرار", outgoing=True))
async def send_button(event):
    user_id = event.sender_id 
    profile_button = KeyboardButtonUserProfile(text="البروفايل", user_id=user_id)
    main_button = KeyboardButton(text="الرئيسي")
    markup = ReplyKeyboardMarkup(
        rows=[
            KeyboardButtonRow(buttons=[profile_button, main_button])
        ],
        resize=True 
    )
    await event.reply("هذه هي الأزرار المطلوبة:", buttons=markup)
