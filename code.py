import os
from telethon import TelegramClient, events
from faster_whisper import WhisperModel
from ABH import *
print("⏳ جاري تحميل نموذج الذكاء الاصطناعي...")
model = WhisperModel("base", device="cpu", compute_type="int8")
print("✅ النموذج جاهز للعمل!")
bot = ABH
@bot.on(events.NewMessage(incoming=True))
async def handle_voice_message(event):
    if event.message.voice or event.message.audio:
        
        # إرسال رسالة للمستخدم تبلغة بالبدء (سلاسة في تجربة المستخدم)
        status_msg = await event.reply("🎙️ جاري تحميل الفويس ومعالجته...")
        
        # تحميل ملف الصوت مؤقتاً
        path = await event.message.download_media(file="temp_voice.ogg")
        
        try:
            await status_msg.edit("⚡ جاري تحويل الصوت إلى كتابة بالذكاء الاصطناعي...")
            
            # بدء معالجة الصوت وترجمته للعربية
            segments, info = model.transcribe(path, language="ar", beam_size=5)
            
            # تجميع النص من المقاطع الصوتية
            full_text = ""
            for segment in segments:
                full_text += segment.text + " "
            
            # إرسال النص النهائي للمستخدم
            if full_text.strip():
                await status_msg.edit(f"📝 **النص المكتوب:**\n\n{full_text}")
            else:
                await status_msg.edit("❌ نعتذر، لم نتمكن من سماع أي كلمات واضحة في الفويس.")
                
        except Exception as e:
            await status_msg.edit(f"❌ حدث خطأ أثناء المعالجة: {str(e)}")
            
        finally:
            # حذف ملف الصوت المؤقت للحفاظ على مساحة الجهاز
            if os.path.exists(path):
                os.remove(path)

print("🤖 البوت يعمل الآن بنجاح... أرسل له أي فويس في تليجرام!")
bot.run_until_disconnected()
