from ABH import *
from art import text2art
import random

# دالة لتجهيز النص الفني لتليجرام
def get_telegram_banner(text):
    # تحويل النص إلى فن ASCII
    ascii_text = text2art(text, font="small") # خط small أفضل للهواتف
    # وضع النص داخل علامات الكود لضمان ترتيب المسافات
    return ascii_text

@ABH.on(events.NewMessage(pattern=r'^البداية$'))
async def start_msg(e):
    banner = get_telegram_banner("ABH")
    
    msg = f"{banner}\n🚀 **أهلاً بك في البوت!**\n\n💡"
    await e.reply(msg)
    
