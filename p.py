import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# متغيرات البيئة
BOT_TOKEN = os.getenv("BOT_TOKEN", "ضع_توكن_البوت")

async def toggle_reactions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.chat.type in ["group", "supergroup"]:
        await update.message.reply_text("هذا الأمر يعمل فقط في المجموعات.")
        return

    if len(context.args) != 1 or context.args[0] not in ["on", "off"]:
        await update.message.reply_text("يرجى استخدام الأمر بالشكل التالي:\n/reactions on أو /reactions off")
        return

    status = context.args[0]

    try:
        await context.bot.set_chat_available_reactions(
            chat_id=update.message.chat_id,
            available_reactions="all" if status == "on" else []
        )
        await update.message.reply_text(
            "تم تفعيل التفاعلات." if status == "on" else "تم تعطيل التفاعلات."
        )
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("reactions", toggle_reactions))
    print("Bot is running...")
    app.run_polling()
