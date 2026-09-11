import asyncio
from datetime import datetime
import json
import os
import random
import re
import warnings

warnings.filterwarnings("ignore")

import joblib
from ABH import ABH as client
from Resources import *
from telethon import Button, events

# 1. تحميل الموديل الذكي
print("⏳ جاري تحميل الموديل...")
MODEL_PATH = "model.joblib"
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("✅ تم تحميل الموديل بنجاح!")
else:
    model = None
    print("⚠️ لم يتم العثور على ملف model.joblib!")


def normalize_arabic_text(text: str) -> str:
    """توحيد النصوص العربية لضمان تطابق الفحص مع تدريب الموديل"""
    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ة\b", "ه", text)
    text = re.sub(r"ى\b", "ي", text)
    text = re.sub(r"[\u064B-\u0652\u0640]", "", text)  # إزالة التشكيل والتطويل
    return text.strip()


def extract_context_understanding(clean_text: str) -> list[tuple[str, float]]:
    """تحليل النص واستخراج أبرز الكلمات التي فهم الموديل أنها سبب البلاغ"""
    if model is None:
        return []

    try:
        # الوصول للـ Pipeline (Vectorizer + Classifier)
        if hasattr(model, "named_steps"):
            vectorizer = model.named_steps.get("vectorizer") or model.steps[0][1]
            classifier = model.named_steps.get("classifier") or model.steps[-1][1]
        else:
            return []

        # تحويل النص إلى مصفوفة خfeatures
        X_vec = vectorizer.transform([clean_text])
        feature_names = vectorizer.get_feature_names_out()

        # استخراج العناصر الموجودة في النص فقط
        nonzero_indices = X_vec.nonzero()[1]

        # تحديد معامات الشدة لكل كلمة بحسب نوع الموديل
        if hasattr(classifier, "coef_"):
            weights = classifier.coef_[0]
        elif hasattr(classifier, "feature_log_prob_"):
            weights = classifier.feature_log_prob_[1] - classifier.feature_log_prob_[0]
        else:
            return []

        word_scores = []
        for idx in nonzero_indices:
            word = feature_names[idx]
            score = weights[idx]
            # نأخذ الكلمات التي أثرت إيجابياً باتجاه تصنيف الإساءة
            if score > 0:
                word_scores.append((word, float(score)))

        # ترتيب الكلمات من الأكثر تأثيراً إلى الأقل
        word_scores.sort(key=lambda x: x[1], reverse=True)
        return word_scores[:3]  # أرجِع أعلى 3 كلمات تأثيراً
    except Exception as e:
        print(f"تعذر استخراج تحليل الكلمات: {e}")
        return []


def _predict_sync(clean_text: str) -> tuple[float, list[tuple[str, float]]]:
    """تنبؤ تزامني ينفذ داخل Thread منفصل مع تحليل فهم الموديل"""
    if model is None:
        return 0.0, []
    try:
        prob = float(model.predict_proba([clean_text])[0][1])
        top_words = extract_context_understanding(clean_text) if prob >= 0.95 else []
        return prob, top_words
    except Exception as e:
        print(f"خطأ أثناء التنبؤ: {e}")
        return 0.0, []


async def check_profanity_ai_only(
    text: str,
) -> tuple[bool, float, str, list[tuple[str, float]]]:
    """دالة الفحص المعتمدة على الذكاء الاصطناعي مع شرح فهم السياق"""
    if not text or not text.strip() or model is None:
        return False, 0.0, "نص فارغ أو الموديل غير محمل", []

    clean_text = normalize_arabic_text(text)
    if not clean_text:
        return False, 0.0, "نص فارغ بعد التنظيف", []

    prob, top_words = await asyncio.to_thread(_predict_sync, clean_text)

    if prob >= 0.95:
        return True, prob, "تكهن الموديل الذكي (ثقة عالية)", top_words

    return False, prob, "نص سليم", []


@client.on(events.NewMessage)
async def monitor_messages(event):
    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False):
        return

    text = event.raw_text
    if not text:
        return

    # فحص الرسالة واستخراج فهم الموديل للسياق
    is_flagged, confidence, reason, top_words = await check_profanity_ai_only(text)

    if is_flagged:
        try:
            # 1. استخراج رابط الرسالة
            chat = await event.get_chat()
            if getattr(chat, "username", None):
                msg_link = f"https://t.me/{chat.username}/{event.id}"
            else:
                clean_chat_id = str(event.chat_id).replace("-100", "")
                msg_link = f"https://t.me/c/{clean_chat_id}/{event.id}"

            # 2. معلومات المرسل
            first_name = sender.first_name or "بدون اسم"
            last_name = f" {sender.last_name}" if sender.last_name else ""
            full_name = f"{first_name}{last_name}"
            username = f"@{sender.username}" if sender.username else "لا يوجد"
            user_id = sender.id

            # 3. صياغة فهم الموديل للسياق
            if top_words:
                words_str = ", ".join([f"`{w[0]}`" for w in top_words])
                ai_understanding = f"فهم الذكاء أن السياق مسيء بناءً على الكلمات: {words_str}"
            else:
                ai_understanding = "فهم الذكاء التركيب العام للجملة وسياقها ككل"

            # 4. إعداد التقرير الإشعاري
            report_text = (
                f"🚨 **رصد كلام بذيء ({confidence * 100:.1f}%)**\n\n"
                f"👤 **معلومات المرسل:**\n"
                f"• **الاسم:** [{full_name}](tg://user?id={user_id})\n"
                f"• **اليوزر:** {username}\n"
                f"• **الآيدي:** `{user_id}`\n\n"
                f"📝 **النص:**\n`{text}`\n\n"
                f"💡 **تفسير الذكاء الاصطناعي للسياق:**\n{ai_understanding}\n\n"
                f"📊 **نسبة التوقع:** `{confidence * 100:.1f}%`\n\n"
                f"🔗 **رابط الرسالة:** [الانتقال للرسالة]({msg_link})"
            )

            # 5. إرسال التقرير
            await client.send_message(wfffp, report_text, link_preview=False)

        except Exception as e:
            print(f"خطأ أثناء إرسال التقرير: {e}")
