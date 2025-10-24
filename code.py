from ABH import ABH as bot
from telethon import TelegramClient, events
import requests
import datetime

# إعدادات البوت


# دالة تحويل الوقت من Unix إلى تاريخ مقروء
def to_date(timestamp):
    if not timestamp:
        return "غير متوفر"
    return datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

# دالة لجلب بيانات اللاعب من Chess.com
def get_chess_profile(username):
    url = f"https://api.chess.com/pub/player/{username.lower()}"
    headers = {"User-Agent": "TelegramChessBot/1.0 (contact@example.com)"}
    r = requests.get(url, headers=headers, timeout=10)

    if r.status_code == 404:
        return None
    elif r.status_code != 200:
        return {"error": f"حدث خطأ أثناء الاتصال: {r.status_code}"}

    return r.json()

# حدث الاستماع للأمر
@bot.on(events.NewMessage(pattern=r"^/chess\s+(\w+)$"))
async def chess_handler(event):
    username = event.pattern_match.group(1)
    await event.respond("⏳ جاري جلب معلومات اللاعب...")

    data = get_chess_profile(username)

    if not data:
        await event.respond("❌ لم يتم العثور على هذا المستخدم على Chess.com.")
        return
    if "error" in data:
        await event.respond(data["error"])
        return

    # تنسيق المعلومات
    profile_text = (
        f"♟ **معلومات اللاعب Chess.com** ♟\n\n"
        f"👤 **الاسم:** {data.get('username', 'غير متوفر')}\n"
        f"🏆 **اللقب:** {data.get('title', 'بدون')}\n"
        f"🌍 **الدولة:** {data.get('country', '').split('/')[-1] if data.get('country') else 'غير معروف'}\n"
        f"📅 **تاريخ الانضمام:** {to_date(data.get('joined'))}\n"
        f"🕐 **آخر ظهور:** {to_date(data.get('last_online'))}\n"
        f"🔗 [الملف الشخصي على Chess.com]({data.get('url')})"
    )

    await event.respond(profile_text, link_preview=False)

print("✅ البوت يعمل الآن...")
