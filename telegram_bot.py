import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from agent_orchestrator import run_agent_telegram

load_dotenv()

USER_SESSIONS = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sentinel Online.\nTell me what to do.\nUse /stop to abort a task.")

async def stop_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in USER_SESSIONS and USER_SESSIONS[user_id]["is_running"]:
        USER_SESSIONS[user_id]["is_running"] = False
        await update.message.reply_text("🛑 Session reset. You can start a new task.")
    else:
        await update.message.reply_text("No active task to stop.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.is_bot:
        return
    
    user_id = update.effective_user.id
    user_text = update.message.text

    # 1. Handle Replies (Agent asking a question)
    if user_id in USER_SESSIONS and USER_SESSIONS[user_id]["is_waiting"]:
        USER_SESSIONS[user_id]["last_reply"] = user_text
        USER_SESSIONS[user_id]["input_event"].set()
        return
    
    # 2. Prevent concurrent tasks
    if user_id in USER_SESSIONS and USER_SESSIONS[user_id]["is_running"]:
        await update.message.reply_text("⚠️ Agent is busy. Use /stop to abort.")
        return
    
    # 3. LOCK SESSION IMMEDIATELY
    USER_SESSIONS[user_id] = {
        "is_running": True,
        "is_waiting": False,
        "input_event": asyncio.Event(),
        "last_reply": None
    }

    await update.message.reply_text(f"🚀 Starting task: {user_text}")

    async def telegram_output(text: str):
        if not USER_SESSIONS[user_id]["is_running"]:
            raise asyncio.CancelledError("Stopped by user")

        if "Thinking..." in text: return
        
        max_len = 4000
        for i in range(0, len(text), max_len):
            chunk = text[i:i+max_len]
            try:
                await update.message.reply_text(chunk)
            except Exception as e:
                print(f"Telegram Send Error: {e}")

    async def telegram_input(question: str):
        """Ask user and wait for reply."""
        USER_SESSIONS[user_id]["is_waiting"] = True
        USER_SESSIONS[user_id]["input_event"].clear()

        await update.message.reply_text(f"🔴 <b>QUESTION:</b> {question}\n(Reply to this message)", parse_mode=ParseMode.HTML)

        # Wait for reply
        await USER_SESSIONS[user_id]["input_event"].wait()
        
        USER_SESSIONS[user_id]["is_waiting"] = False
        return USER_SESSIONS[user_id]["last_reply"]

    try:
        await run_agent_telegram(
            user_query=user_text,
            output_handler=telegram_output,
            input_handler=telegram_input,
        )
        await update.message.reply_text("✅ Task Completed.")
    except asyncio.CancelledError:
        await update.message.reply_text("🛑 Task Aborted.")
    except Exception as e:
        if "Stopped by user" in str(e):
             await update.message.reply_text("🛑 Task Aborted.")
        else:
             await update.message.reply_text(f"❌ Error: {str(e)}")
    finally:
        USER_SESSIONS[user_id]["is_running"] = False
        USER_SESSIONS[user_id]["is_waiting"] = False

def run_telegram_bot():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_task))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Telegram Bot Polling...")
    app.run_polling()