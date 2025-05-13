from telethon import TelegramClient, events
import os
import time
import json

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
ABH = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)

# القيم المتوقعة للعبة
WIN_VALUES = {
    "🎲": 6,
    "🎯": 6,
    "🏀": 5,
    "⚽": 5,
    "🎳": 6,
    "🎰": 64
}

# مسار ملف تخزين بيانات المستخدم
USER_DATA_FILE = "user_data.json"

# دالة لتحميل بيانات المستخدمين من ملف
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

# دالة لتخزين بيانات المستخدمين في ملف
def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# التعامل مع الحدث الجديد (الرسائل)
@ABH.on(events.NewMessage(pattern=r'.*'))
async def telegramgames(event):
    if not event.message.dice:
        return
    
    # الحصول على بيانات الرسالة
    user_id = event.sender_id
    dice = event.message.dice
    emoji = dice.emoticon
    value = dice.value
    print(f"📥 تلقينا لعبة: {emoji} | القيمة: {value}")

    # تحميل بيانات المستخدمين من الملف
    user_data = load_user_data()

    # تحقق من الوقت الأخير الذي لعب فيه المستخدم
    last_play_time = user_data.get(str(user_id), {}).get("last_play_time", 0)

    # حساب الوقت الحالي
    current_time = int(time.time())

    # الفاصل الزمني بين كل لعبتين (في هذه الحالة 5 دقائق)
    time_diff = current_time - last_play_time
    if time_diff < 5 * 60:  # 5 دقائق بالثواني
        # إذا لم يمضِ 5 دقائق، إظهار رسالة للمستخدم بالانتظار
        wait_time = (5 * 60 - time_diff) // 60  # الوقت المتبقي بالدقائق
        await event.reply(f"🚫 يجب عليك الانتظار {wait_time} دقيقة{'s' if wait_time > 1 else ''} قبل اللعب مجددًا.")
        return

    # إذا مر الوقت الكافي، فإعطاء فرصة للعب
    win = value == WIN_VALUES.get(emoji, -1)
    if win:
        await event.reply(f"🎉 مبروك! فزت في لعبة {emoji}\n🔢 النتيجة: `{value}`")
    else:
        await event.reply(f"💔 للأسف، لم تفز في لعبة {emoji}\n🔢 النتيجة: `{value}`")

    # تحديث وقت اللعب في بيانات المستخدم
    user_data[str(user_id)] = {"last_play_time": current_time}
    save_user_data(user_data)

if __name__ == "__main__":
    print("✅ بدأ البوت بنجاح ...")
    ABH.run_until_disconnected()
