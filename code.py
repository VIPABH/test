from ABH import *
import ast
from pathlib import Path
client = ABH
# --- 1. تحديث منطق إعادة تنظيم المتغيرات ---
def reorder_code_variables(source_code: str) -> str:
    """يقوم بنقل جميع تعريفات المتغيرات (Assign/AnnAssign) إلى أعلى الملف وترتيبها أبجدياً."""
    tree = ast.parse(source_code)
    
    variables = []
    others = []
    
    for node in tree.body:
        # تحديد ما إذا كان السطر هو تعريف متغير (Assign or AnnAssign)
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            variables.append(node)
        else:
            others.append(node)
            
    # ترتيب المتغيرات أبجدياً حسب الاسم
    def get_var_name(node):
        if isinstance(node, ast.Assign):
            return node.targets[0].id if isinstance(node.targets[0], ast.Name) else "z"
        return node.target.id if isinstance(node.target, ast.Name) else "z"
        
    variables.sort(key=get_var_name)
    
    # دمج المتغيرات في الأعلى ثم باقي الكود
    tree.body = variables + others
    return ast.unparse(tree)

# --- 2. تحديث أمر /analyze ---
@client.on(events.NewMessage(pattern=r"/analyze"))
async def handle_analyze(event):
    reply = await event.get_reply_message()
    if not reply or not reply.file:
        return await event.respond("يرجى الرد على ملف .py")

    tmp_path = await reply.download_media()
    with open(tmp_path, "r", encoding="utf-8") as f:
        code = f.read()
    
    # إعادة التنظيم
    new_code = reorder_code_variables(code)
    
    # حفظ وإرسال الملف المنظم
    output_path = "reordered_code.py"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_code)
        
    await event.respond("✅ تم تنظيم المتغيرات في الأعلى:", file=output_path)
    os.remove(tmp_path)
    os.remove(output_path)

# --- 3. تحديث أمر /count ---
# ملاحظة: إذا كنت تقصد أن البوت يقوم بمسح مجلد العمل الحالي (حيث يعمل البوت) 
# فأنت لست بحاجة إلى ملف zip، يمكنك مسح المجلد مباشرة:
@client.on(events.NewMessage(pattern=r"/count_here"))
async def handle_count_current(event):
    # يقوم بمسح المسار الحالي للملف حيث يعمل السكربت
    current_path = os.getcwd() 
    report = count_project_text(current_path)
    await send_long_text(event, report, "project_report.txt")
