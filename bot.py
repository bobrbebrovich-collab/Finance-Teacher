import os
import logging
from groq import Groq

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# ===== ENV =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "8383746618"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing (set env BOT_TOKEN)")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is missing (set env GROQ_API_KEY)")

# ===== GROQ CLIENT =====
client = Groq(api_key=GROQ_API_KEY)

# ===== LOGGING =====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== MEMORY =====
user_histories: dict[int, list[dict]] = {}

SYSTEM_PROMPT = """Ты личный учитель по финансам и бизнесу. Твоя задача — подготовить студента к работе в Coinbase на позициях Business Strategy, Business Development и Finance Analyst.

Правила:
- Объясняй как опытный школьный учитель — просто, понятно, с примерами
- После каждой темы задавай 1-2 вопроса чтобы проверить понимание
- Если студент ошибается — мягко поправляй и объясняй правильный ответ
- Давай домашние задания и практические задачи
- Веди учёт прогресса студента
- Темы: финансовый анализ, бизнес-стратегия, крипторынок, бизнес-модели Coinbase, метрики, P&L, unit economics, DCF, market sizing, competitive analysis
- Отвечай на русском языке
- Будь строгим но справедливым учителем"""

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📚 Новая тема"), KeyboardButton("📝 Тест")],
        [KeyboardButton("📊 Мой прогресс"), KeyboardButton("🏠 Домашнее задание")],
    ],
    resize_keyboard=True
)

def _ensure_history(user_id: int):
    if user_id not in user_histories:
        user_histories[user_id] = []

def _trim_history(user_id: int, limit: int = 20):
    if len(user_histories[user_id]) > limit:
        user_histories[user_id] = user_histories[user_id][-limit:]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text(
        "👋 Привет! Я твой личный учитель по финансам и бизнесу.\n\n"
        "Моя цель — подготовить тебя к работе в Coinbase на позициях:\n"
        "• Business Strategy\n"
        "• Business Development\n"
        "• Finance Analyst\n\n"
        "Давай начнём! С чего хочешь начать, или напиши любой вопрос по теме.",
        reply_markup=MAIN_KEYBOARD
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    text = msg.text or ""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not text.strip():
        return

    _ensure_history(user_id)

    # кнопки -> команды
    if text == "📚 Новая тема":
        text = "Дай мне новую тему для изучения, подходящую для моего уровня"
    elif text == "📝 Тест":
        text = "Проведи короткий тест по последней теме, которую мы изучали"
    elif text == "📊 Мой прогресс":
        text = "Расскажи о моём прогрессе — что я уже изучил и что осталось"
    elif text == "🏠 Домашнее задание":
        text = "Дай мне домашнее задание по текущей теме"

    user_histories[user_id].append({"role": "user", "content": text})
    _trim_history(user_id)

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + user_histories[user_id],
            max_tokens=1000,
            temperature=0.7,
        )
        reply = response.choices[0].message.content or "⚠️ Пустой ответ модели."

        user_histories[user_id].append({"role": "assistant", "content": reply})
        _trim_history(user_id)

        await msg.reply_text(reply, reply_markup=MAIN_KEYBOARD)

    except Exception as e:
        logger.exception("Groq error")
        await msg.reply_text("⚠️ Ошибка, попробуй ещё раз.", reply_markup=MAIN_KEYBOARD)

def main():
    print("BOT VERSION: rebuilt-26-02")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Бот-учитель запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
  
