from telethon import events
from ABH import *
import os
import shutil
import zipfile
import tempfile
from pathlib import Path
"""
منطق التحليل المشترك: يُستخدم من طرف telegram_bot.py
- analyze_file_text(path)   -> تقرير نصي لملف بايثون واحد
- count_project_text(path)  -> تقرير نصي لعدد التعريفات/الاستخدامات في مشروع كامل
"""

import ast
from pathlib import Path
from collections import Counter


# ---------------------------------------------------------------------
# الجزء الأول: تحليل ملف واحد
# ---------------------------------------------------------------------

def analyze_file(filepath: str) -> dict:
    source = Path(filepath).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=filepath)

    variables, functions, classes = [], [], []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append({
                "name": node.name,
                "line": node.lineno,
                "args": [a.arg for a in node.args.args],
            })
        elif isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "line": node.lineno,
                "bases": [b.id for b in node.bases if isinstance(b, ast.Name)],
            })
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variables.append({"name": target.id, "line": node.lineno})
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                variables.append({"name": node.target.id, "line": node.lineno})

    def dedup_sort(items):
        seen = {}
        for it in items:
            seen.setdefault(it["name"], it)
        return sorted(seen.values(), key=lambda x: x["name"].lower())

    return {
        "classes": dedup_sort(classes),
        "functions": dedup_sort(functions),
        "variables": dedup_sort(variables),
    }


def format_file_report(result: dict) -> str:
    lines = []
    lines.append(f"📦 الكلاسات ({len(result['classes'])})")
    for c in result["classes"]:
        bases = f"({', '.join(c['bases'])})" if c["bases"] else ""
        lines.append(f"  • {c['name']}{bases}   [سطر {c['line']}]")

    lines.append(f"\n🔧 الدوال ({len(result['functions'])})")
    for f in result["functions"]:
        args = ", ".join(f["args"])
        lines.append(f"  • {f['name']}({args})   [سطر {f['line']}]")

    lines.append(f"\n🔤 المتغيرات ({len(result['variables'])})")
    for v in result["variables"]:
        lines.append(f"  • {v['name']}   [سطر {v['line']}]")

    return "\n".join(lines)


def analyze_file_text(filepath: str) -> str:
    result = analyze_file(filepath)
    return format_file_report(result)


# ---------------------------------------------------------------------
# الجزء الثاني: عدّ التعريفات/الاستخدامات في مشروع كامل
# ---------------------------------------------------------------------

class ProjectCounter(ast.NodeVisitor):
    def __init__(self):
        self.func_defs = Counter()
        self.class_defs = Counter()
        self.var_defs = Counter()
        self.func_calls = Counter()
        self.class_uses = Counter()
        self.var_uses = Counter()

        self._known_funcs = set()
        self._known_classes = set()

    def visit_FunctionDef(self, node):
        self.func_defs[node.name] += 1
        self._known_funcs.add(node.name)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.class_defs[node.name] += 1
        self._known_classes.add(node.name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.var_defs[target.id] += 1
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name):
            self.var_defs[node.target.id] += 1
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            name = node.func.id
            if name in self._known_classes:
                self.class_uses[name] += 1
            else:
                self.func_calls[name] += 1
        elif isinstance(node.func, ast.Attribute):
            self.func_calls[node.func.attr] += 1
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if node.id not in self._known_funcs and node.id not in self._known_classes:
                self.var_uses[node.id] += 1
        self.generic_visit(node)


def scan_project(project_path: str):
    counter = ProjectCounter()
    py_files = list(Path(project_path).rglob("*.py"))
    warnings = []

    for pyfile in py_files:
        try:
            source = pyfile.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(pyfile))
            counter.visit(tree)
        except (SyntaxError, UnicodeDecodeError) as e:
            warnings.append(f"تعذر تحليل {pyfile.name}: {e}")

    return counter, len(py_files), warnings


def format_project_report(counter: ProjectCounter, files_count: int, warnings: list) -> str:
    lines = [f"تم فحص {files_count} ملف بايثون"]

    if warnings:
        lines.append("\n⚠️ تحذيرات:")
        lines.extend(f"  - {w}" for w in warnings)

    lines.append(
        f"\n📦 الكلاسات — تعريفات: {sum(counter.class_defs.values())} "
        f"| استخدامات: {sum(counter.class_uses.values())}"
    )
    for name, count in counter.class_defs.most_common():
        uses = counter.class_uses.get(name, 0)
        lines.append(f"  • {name}: تعريف {count} | استخدام {uses}")

    lines.append(
        f"\n🔧 الدوال — تعريفات: {sum(counter.func_defs.values())} "
        f"| استدعاءات: {sum(counter.func_calls.values())}"
    )
    for name, count in counter.func_defs.most_common():
        calls = counter.func_calls.get(name, 0)
        lines.append(f"  • {name}: تعريف {count} | استدعاء {calls}")

    lines.append(
        f"\n🔤 المتغيرات — تعريفات: {sum(counter.var_defs.values())} "
        f"| استخدامات: {sum(counter.var_uses.values())}"
    )
    for name, count in counter.var_defs.most_common():
        uses = counter.var_uses.get(name, 0)
        lines.append(f"  • {name}: تعريف {count} | استخدام {uses}")

    return "\n".join(lines)


def count_project_text(project_path: str) -> str:
    counter, files_count, warnings = scan_project(project_path)
    return format_project_report(counter, files_count, warnings)
TELEGRAM_MAX_LEN = 4000
client = ABH
async def send_long_text(event, text: str, filename_if_long: str) -> None:
    """يبعث النص كرسالة عادية، أو كملف لو كان طويل جدًا."""
    if len(text) <= TELEGRAM_MAX_LEN:
        await event.respond(f"```\n{text}\n```")
        return

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(text)
        tmp_path = tmp.name

    await event.respond(
        "التقرير طويل، تم إرساله كملف 👇",
        file=tmp_path,
    )
    os.remove(tmp_path)


@client.on(events.NewMessage(pattern=r"/analyze"))
async def handle_analyze(event):
    reply = await event.get_reply_message()
    if not reply or not reply.file or not (reply.file.name or "").endswith(".py"):
        await event.respond(
            "استخدم الأمر كرد (reply) على رسالة فيها ملف بايثون (.py)."
        )
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = await reply.download_media(file=tmpdir)
        try:
            report = analyze_file_text(file_path)
        except SyntaxError as e:
            await event.respond(f"⚠️ خطأ في تحليل الملف: {e}")
            return

    await send_long_text(event, report, "analyze_report.txt")


@client.on(events.NewMessage(pattern=r"/count"))
async def handle_count(event):
    reply = await event.get_reply_message()
    if not reply or not reply.file or not (reply.file.name or "").endswith(".zip"):
        await event.respond(
            "استخدم الأمر كرد (reply) على رسالة فيها ملف مضغوط (.zip) للمشروع كامل."
        )
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = await reply.download_media(file=tmpdir)
        extract_dir = Path(tmpdir) / "project"
        extract_dir.mkdir()

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)
        except zipfile.BadZipFile:
            await event.respond("⚠️ الملف المرفق ليس ملف zip صالح.")
            return

        report = count_project_text(str(extract_dir))

    await send_long_text(event, report, "count_report.txt")
