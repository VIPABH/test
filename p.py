import os
import random

# اسم الملف لتخزين النقاط
POINTS_FILE = "points.txt"

# قائمة الأسئلة والأجوبة
QUESTIONS = [
    ("ما عاصمة العراق؟", "بغداد"),
    ("كم عدد الكواكب في المجموعة الشمسية؟", "8"),
    ("ما هو حاصل ضرب 5 × 6؟", "30"),
    ("من هو مخترع المصباح الكهربائي؟", "توماس إديسون"),
    ("ما هو الحيوان الذي ينام واقفًا؟", "الحصان"),
]

# التحقق من وجود الملف، وإذا لم يكن موجودًا يتم إنشاؤه
if not os.path.exists(POINTS_FILE):
    with open(POINTS_FILE, "w") as f:
        f.write("0")
    print("📁 تم إنشاء ملف النقاط بنجاح!")

# دالة لقراءة النقاط
def get_points():
    with open(POINTS_FILE, "r") as f:
        return int(f.read().strip())

# دالة لحفظ النقاط الجديدة
def save_points(points):
    with open(POINTS_FILE, "w") as f:
        f.write(str(points))

# دالة لطرح سؤال وإذا كانت الإجابة صحيحة يضيف نقطة
def ask_question():
    question, correct_answer = random.choice(QUESTIONS)
    print(f"\n🧐 سؤال: {question}")
    answer = input("✍️ أدخل إجابتك: ").strip()

    if answer.lower() == correct_answer.lower():
        new_points = get_points() + 1
        save_points(new_points)
        print(f"✅ إجابة صحيحة! 🎉 تم إضافة نقطة. النقاط الحالية: {new_points}")
    else:
        print(f"❌ إجابة خاطئة! الإجابة الصحيحة: {correct_answer}")

# دالة لعرض النقاط
def show_points():
    points = get_points()
    print(f"📊 عدد النقاط الحالية: {points}")

# القائمة الرئيسية
while True:
    print("\nاختر: [1] سؤال 🎯 | [2] عرض النقاط 📊 | [3] خروج ❌")
    choice = input("👉 أدخل رقم الخيار: ")

    if choice == "1":
        ask_question()
    elif choice == "2":
        show_points()
    elif choice == "3":
        print("👋 تم الخروج من البرنامج.")
        break
    else:
        print("🚨 خيار غير صحيح، حاول مرة أخرى!")
