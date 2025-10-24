from ABH import ABH as bot
from telethon import events
import requests, datetime

def to_date(timestamp):
    if not timestamp: return "غير متوفر"
    return datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

def get_chess_profile(username):
    base=f"https://api.chess.com/pub/player/{username.lower()}"
    headers={"User-Agent":"TelegramChessBot/1.0 (contact@example.com)"}
    profile=requests.get(base,headers=headers,timeout=10)
    if profile.status_code==404: return None
    if profile.status_code!=200: return {"error":f"خطأ: {profile.status_code}"}
    stats=requests.get(f"{base}/stats",headers=headers,timeout=10)
    stats_data=stats.json() if stats.status_code==200 else {}
    data=profile.json()
    data["stats"]=stats_data
    return data

@bot.on(events.NewMessage(pattern=r"^/chess\s+(\w+)$"))
async def chess_handler(event):
    username=event.pattern_match.group(1)
    await event.respond("⏳ جاري جلب معلومات اللاعب...")
    data=get_chess_profile(username)
    if not data:
        await event.respond("❌ لم يتم العثور على هذا المستخدم على Chess.com.");return
    if "error" in data:
        await event.respond(data["error"]);return
    s=data.get("stats",{})
    def rating(mode):
        try:
            r=s[f"chess_{mode}"]["last"]["rating"]
            elo=s[f"chess_{mode}"]["best"]["rating"]
            return f"{r} (Elo: {elo})"
        except: return "غير متوفر"
    profile_text=(
        f"♟ **معلومات اللاعب Chess.com** ♟\n\n"
        f"👤 **الاسم:** {data.get('username','غير متوفر')}\n"
        f"🏆 **اللقب:** {data.get('title','بدون')}\n"
        f"🌍 **الدولة:** {data.get('country','').split('/')[-1] if data.get('country') else 'غير معروف'}\n"
        f"📅 **تاريخ الانضمام:** {to_date(data.get('joined'))}\n"
        f"🕐 **آخر ظهور:** {to_date(data.get('last_online'))}\n\n"
        f"📊 **التصنيفات:**\n"
        f"⚡ Blitz: {rating('blitz')}\n"
        f"🔥 Bullet: {rating('bullet')}\n"
        f"⏱ Rapid: {rating('rapid')}\n"
        f"🧩 Puzzle: {rating('puzzle')}\n"
        f"📬 Daily: {rating('daily')}\n\n"
        f"🔗 [الملف الشخصي على Chess.com]({data.get('url')})"
    )
    await event.respond(profile_text,link_preview=False)

print("✅ البوت يعمل الآن...")
