import os
import tempfile
import speech_recognition as sr
from telethon import events
from pydub import AudioSegment
import pyttsx3
from ABH import ABH  # استيراد الكلاينت من ملف ABH.py

# ===== إعداد الصوت =====
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# محاولة اختيار صوت عربي (إن وجد)
for voice in engine.getProperty('voices'):
    if "ar" in voice.id.lower() or "arabic" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

# ===== تحويل الصوت إلى نص =====
def speech_to_text(path):
    r = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio = r.record(source)
    try:
        text = r.recognize_sphinx(audio, language="ar")
        return text
    except sr.UnknownValueError:
        return "❌ لم أفهم الصوت"
    except Exception as e:
        return f"⚠️ خطأ أثناء التعرف: {e}"

# ===== تحويل النص إلى صوت =====
def text_to_speech(text, out_path):
    engine.save_to_file(text, out_path)
    engine.runAndWait()
    return out_path

# ===== أمر تحويل الصوت إلى نص =====
@ABH.on(events.NewMessage(pattern=r"^/transcribe$"))
async def transcribe_audio(event):
    if not event.is_reply:
        await event.reply("🎙️ استخدم الأمر بالرد على رسالة صوتية.")
        return

    reply = await event.get_reply_message()
    if not reply.media:
        await event.reply("❌ لا توجد وسائط صوتية.")
        return

    await event.reply("🔍 جاري التعرف على الكلام...")

    with tempfile.TemporaryDirectory() as tmp:
        ogg_path = os.path.join(tmp, "voice.ogg")
        wav_path = os.path.join(tmp, "voice.wav")

        await ABH.download_media(reply, file=ogg_path)

        sound = AudioSegment.from_file(ogg_path)
        sound = sound.set_frame_rate(16000).set_channels(1)
        sound.export(wav_path, format="wav")

        text = speech_to_text(wav_path)
        await event.reply(f"📝 النص:\n{text}")

# ===== أمر تحويل النص إلى صوت =====
from pydub import AudioSegment

@ABH.on(events.NewMessage(pattern=r"^/say$"))
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
        wav_path = os.path.join(tmp, "tts.wav")
        mp3_path = os.path.join(tmp, "tts.mp3")

        # توليد الصوت بصيغة WAV
        text_to_speech(text, wav_path)

        # تحويل WAV إلى MP3 ليقبلها Telegram
        audio = AudioSegment.from_wav(wav_path)
        audio.export(mp3_path, format="mp3")

        # إرسال الملف إلى Telegram
        await event.reply(file=mp3_path)
