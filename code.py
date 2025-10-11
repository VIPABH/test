import os
from telethon import events
from ABH import ABH as client
import os
import asyncio
import tempfile
import speech_recognition as sr
from telethon import TelegramClient, events
from pydub import AudioSegment
import pyttsx3

# ===== إعدادات Telethon =====

# ===== إعداد مكتبة تحويل النص إلى صوت =====
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # سرعة الصوت
voices = engine.getProperty('voices')

# محاولة تعيين صوت عربي إن وجد
for voice in voices:
    if "ar" in voice.id.lower() or "arabic" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

# ===== تحويل الصوت إلى نص =====
def speech_to_text(path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_sphinx(audio, language="ar")
        return text
    except sr.UnknownValueError:
        return "❌ لم أتمكن من فهم الصوت"
    except Exception as e:
        return f"⚠️ حدث خطأ أثناء التعرف: {e}"

# ===== تحويل النص إلى صوت =====
def text_to_speech(text, out_path):
    engine.save_to_file(text, out_path)
    engine.runAndWait()
    return out_path

# ===== أمر تحويل الصوت إلى نص =====
@client.on(events.NewMessage(pattern=r"^/transcribe$"))
async def transcribe_audio(event):
    if not event.is_reply:
        await event.reply("🎙️ استخدم الأمر بالرد على رسالة صوتية.")
        return

    reply = await event.get_reply_message()
    if not reply.media:
        await event.reply("❌ لا توجد وسائط صوتية.")
        return

    await event.reply("🔍 جاري تحويل الصوت إلى نص...")

    with tempfile.TemporaryDirectory() as tmp:
        ogg_path = os.path.join(tmp, "voice.ogg")
        wav_path = os.path.join(tmp, "voice.wav")

        await client.download_media(reply, file=ogg_path)

        # تحويل OGG إلى WAV (يدعمه Sphinx)
        sound = AudioSegment.from_file(ogg_path)
        sound = sound.set_frame_rate(16000).set_channels(1)
        sound.export(wav_path, format="wav")

        text = speech_to_text(wav_path)
        await event.reply(f"📝 النص:\n{text}")

# ===== أمر تحويل النص إلى صوت =====
@client.on(events.NewMessage(pattern=r"^/say$"))
async def say_text(event):
    if not event.is_reply:
        await event.reply("💬 استخدم الأمر بالرد على رسالة نصية.")
        return

    reply = await event.get_reply_message()
    if not reply.text:
        await event.reply("❌ لا يوجد نص لتحويله إلى صوت.")
        return

    text = reply.text
    await event.reply("🎧 جاري تحويل النص إلى صوت...")

    with tempfile.TemporaryDirectory() as tmp:
        out_path = os.path.join(tmp, "tts.wav")
        text_to_speech(text, out_path)
        await event.reply(file=out_path)

# ===== تشغيل البوت =====
