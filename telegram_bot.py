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
        USER_SESSIONS[user_id]["is_waiting"] = False
        USER_SESSIONS[user_id]["input_event"].set()
        await update.message.reply_text("🛑 Session reset. You can start a new task.")
    else:
        await update.message.reply_text("No active task to stop.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.is_bot:
        return
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    user_text = update.message.text

    # 1. Handle Replies (Agent asking a question)
    if user_id in USER_SESSIONS and USER_SESSIONS[user_id]["is_waiting"]:
        USER_SESSIONS[user_id]["last_reply"] = user_text
        USER_SESSIONS[user_id]["is_waiting"] = False
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
        "last_reply": None,
        "chat_id": chat_id,
        "task": None
    }

    await update.message.reply_text(f"🚀 Starting task: {user_text}")

    async def wrapper():
        try:
            await run_agent_telegram(
                user_query=user_text,
                output_handler=telegram_output,
                input_handler=telegram_input,
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ Task Completed."
            )
        except asyncio.CancelledError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🛑 Task Aborted."
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Error: {str(e)}"
            )
        finally:
            if user_id in USER_SESSIONS:
                USER_SESSIONS[user_id]["is_running"] = False
                USER_SESSIONS[user_id]["is_waiting"] = False
    
    USER_SESSIONS[user_id]["task"] = asyncio.create_task(wrapper())

    async def telegram_output(text: str):
        if not USER_SESSIONS[user_id]["is_running"]:
            raise asyncio.CancelledError("Stopped by user")
        
        session = USER_SESSIONS[user_id]
        chat_id = session["chat_id"]
        
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

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
        session = USER_SESSIONS[user_id]
        chat_id = session["chat_id"]

        session["is_waiting"] = True
        session["input_event"].clear()

        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🔴 <b>QUESTION:</b> {question}\n(Reply to this message)",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            print(f"Failed to send question: {e}")
            session["is_waiting"] = False
            return "Error: could not ask question"
        
        # Wait for reply
        await session["input_event"].wait()
        
        session["is_waiting"] = False
        return session.get("last_reply", "No reply received")

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