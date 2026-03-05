import os
import logging
from groq import Groq
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# ------------------- LOGGING -------------------
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ------------------- ENV KEYS -------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN:
    raise RuntimeError("Не задан TELEGRAM_TOKEN в Railway Variables")
if not GROQ_API_KEY:
    raise RuntimeError("Не задан GROQ_API_KEY в Railway Variables")

client = Groq(api_key=GROQ_API_KEY)
chat_histories = {}

# ------------------- SYSTEM PROMPT -------------------
SYSTEM_PROMPT = """
Ты — личный репетитор по бизнесу, аналитике и финтеху. Твоя главная цель — подготовить ученика 18 лет к роли Junior Analyst / BizOps в Coinbase или аналогичной крипто/tech компании.

ПРОГРАММА ОБУЧЕНИЯ (7 модулей):

МОДУЛЬ 1 — Как работает бизнес
  Урок 1.1: Как устроена компания (структура, роли, отделы)
  Урок 1.2: Бизнес-модели — как компании зарабатывают деньги
  Урок 1.3: Юнит-экономика — считаем прибыль на одного клиента
  Урок 1.4: P&L — отчёт о прибылях и убытках
  Урок 1.5: Как читать финансовую отчётность

МОДУЛЬ 2 — Бизнес-стратегия
  Урок 2.1: Что такое стратегия и зачем она нужна
  Урок 2.2: SWOT-анализ — оцениваем любой бизнес за 10 минут
  Урок 2.3: Porter's 5 Forces — анализ конкурентной среды
  Урок 2.4: TAM / SAM / SOM — считаем размер рынка
  Урок 2.5: Go-to-market стратегия — как выходить на рынок
  Урок 2.6: Competitive analysis — как анализировать конкурентов
  Урок 2.7: Как менять нишу — переносим навыки из одной индустрии в другую
  Урок 2.8: Стратегия Coinbase — разбираем реальный кейс

МОДУЛЬ 3 — Аналитика и метрики
  Урок 3.1: Основные бизнес-метрики (MAU, DAU, Churn, LTV, CAC)
  Урок 3.2: Воронка продаж и конверсия
  Урок 3.3: SQL — основы (SELECT, WHERE, GROUP BY)
  Урок 3.4: SQL — продвинутый (JOIN, подзапросы, оконные функции)
  Урок 3.5: Excel / Google Sheets для аналитика
  Урок 3.6: Как строить дашборды и презентовать данные

МОДУЛЬ 4 — Финтех и крипто
  Урок 4.1: Как работают традиционные финансы (банки, платежи)
  Урок 4.2: Что такое блокчейн и крипто (простым языком)
  Урок 4.3: Как работает Coinbase — бизнес-модель, продукты, выручка
  Урок 4.4: DeFi — децентрализованные финансы
  Урок 4.5: Регуляции в крипто — что важно знать аналитику
  Урок 4.6: Крипто-метрики (TVL, trading volume, active wallets)

МОДУЛЬ 5 — Продуктовое мышление
  Урок 5.1: Что такое продукт и как его строят
  Урок 5.2: Product metrics — как измерить успех продукта
  Урок 5.3: A/B тесты — как принимают решения в tech
  Урок 5.4: User journey и боли пользователя
  Урок 5.5: Как писать PRD (Product Requirements Document)

МОДУЛЬ 6 — BizOps на практике
  Урок 6.1: Что делает BizOps каждый день
  Урок 6.2: Как приоритизировать задачи (RICE, MoSCoW)
  Урок 6.3: Процессы и операционная эффективность
  Урок 6.4: Работа с данными для принятия решений
  Урок 6.5: Стейкхолдеры — как работать с разными командами

МОДУЛЬ 7 — Подготовка к Coinbase
  Урок 7.1: Как устроен процесс найма в Coinbase
  Урок 7.2: Типичные вопросы на интервью (behavioural)
  Урок 7.3: Бизнес-кейсы — как решать и презентовать
  Урок 7.4: SQL задачи с реальных интервью
  Урок 7.5: Как написать резюме и cover letter для Coinbase
  Урок 7.6: Финальный mock-интервью

КАК ВЕСТИ УРОКИ:
1) Начинай урок с названия темы и зачем она нужна для Coinbase
2) Объясняй по структуре:
   🔷 Что это
   🔷 Зачем нужно (связь с Coinbase/крипто/tech)
   🔷 Пример из реальной жизни
   🔷 Как применяется в других нишах
   🔷 Типичная ошибка новичка
   🔷 Мини-вопрос на проверку
3) Не переходи к следующей теме пока ученик не ответил правильно
4) ОБЯЗАТЕЛЬНО: в конце каждого урока давай домашнее задание в формате:
   📝 ДОМАШНЕЕ ЗАДАНИЕ:
   [конкретное практическое задание связанное с темой урока]
   Когда сделаешь — напиши мне результат!
5) После домашнего задания предложи следующий урок

ПРАВИЛА ОБЩЕНИЯ:
- Простые слова, без жаргона (или объясняй термин сразу)
- Коротко и по делу — не пиши стены текста
- Дружелюбно и мотивирующе
- Если пишет "не понял" — объясни через аналогию из жизни
- Отвечай на том же языке на котором пишет ученик
- Цель — Coinbase 🎯
"""

# ------------------- MODULES -------------------
MODULES = {
    "1": {
        "name": "📘 Модуль 1 — Как работает бизнес",
        "lessons": [
            ("1.1", "Как устроена компания"),
            ("1.2", "Бизнес-модели"),
            ("1.3", "Юнит-экономика"),
            ("1.4", "P&L отчёт"),
            ("1.5", "Финансовая отчётность"),
        ],
    },
    "2": {
        "name": "📗 Модуль 2 — Бизнес-стратегия",
        "lessons": [
            ("2.1", "Что такое стратегия"),
            ("2.2", "SWOT-анализ"),
            ("2.3", "Porter's 5 Forces"),
            ("2.4", "TAM/SAM/SOM"),
            ("2.5", "Go-to-market"),
            ("2.6", "Competitive analysis"),
            ("2.7", "Смена ниши"),
            ("2.8", "Кейс Coinbase"),
        ],
    },
    "3": {
        "name": "📊 Модуль 3 — Аналитика и SQL",
        "lessons": [
            ("3.1", "Бизнес-метрики"),
            ("3.2", "Воронка продаж"),
            ("3.3", "SQL основы"),
            ("3.4", "SQL продвинутый"),
            ("3.5", "Excel / Sheets"),
            ("3.6", "Дашборды"),
        ],
    },
    "4": {
        "name": "💰 Модуль 4 — Финтех и крипто",
        "lessons": [
            ("4.1", "Традиционные финансы"),
            ("4.2", "Блокчейн и крипто"),
            ("4.3", "Как работает Coinbase"),
            ("4.4", "DeFi"),
            ("4.5", "Регуляции в крипто"),
            ("4.6", "Крипто-метрики"),
        ],
    },
    "5": {
        "name": "🚀 Модуль 5 — Продукт",
        "lessons": [
            ("5.1", "Что такое продукт"),
            ("5.2", "Product metrics"),
            ("5.3", "A/B тесты"),
            ("5.4", "User journey"),
            ("5.5", "PRD документ"),
        ],
    },
    "6": {
        "name": "⚙️ Модуль 6 — BizOps",
        "lessons": [
            ("6.1", "Что делает BizOps"),
            ("6.2", "Приоритизация задач"),
            ("6.3", "Операционная эффективность"),
            ("6.4", "Данные для решений"),
            ("6.5", "Работа со стейкхолдерами"),
        ],
    },
    "7": {
        "name": "🎯 Модуль 7 — Подготовка к Coinbase",
        "lessons": [
            ("7.1", "Процесс найма Coinbase"),
            ("7.2", "Behavioural вопросы"),
            ("7.3", "Бизнес-кейсы"),
            ("7.4", "SQL на интервью"),
            ("7.5", "Резюме и cover letter"),
            ("7.6", "Mock-интервью"),
        ],
    },
}

# ------------------- KEYBOARDS -------------------
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📚 Все уроки", callback_data="show_modules")],
        [InlineKeyboardButton("▶️ Начать обучение", callback_data="lesson_1.1")],
        [InlineKeyboardButton("🔄 Сбросить историю", callback_data="reset")],
    ]
    return InlineKeyboardMarkup(keyboard)

def modules_keyboard():
    keyboard = []
    for mod_id, mod_data in MODULES.items():
        keyboard.append([InlineKeyboardButton(mod_data["name"], callback_data=f"module_{mod_id}")])
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def lessons_keyboard(module_id: str):
    module = MODULES[module_id]
    keyboard = []
    for lesson_id, lesson_name in module["lessons"]:
        keyboard.append([InlineKeyboardButton(f"📖 {lesson_id} — {lesson_name}", callback_data=f"lesson_{lesson_id}")])
    keyboard.append([InlineKeyboardButton("⬅️ Назад к модулям", callback_data="show_modules")])
    return InlineKeyboardMarkup(keyboard)

# ------------------- HELPERS -------------------
async def send_long_text(bot, chat_id: int, text: str, reply_markup=None, chunk_size: int = 3500):
    # Telegram лимит 4096 символов -> режем с запасом
    if not text:
        text = "(пустой ответ)"
    for i in range(0, len(text), chunk_size):
        part = text[i:i + chunk_size]
        await bot.send_message(chat_id=chat_id, text=part, reply_markup=reply_markup if i == 0 else None)

def get_user_history(user_id: int):
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    return chat_histories[user_id]

def trim_history(history, max_items: int = 30):
    if len(history) > max_items:
        return history[-max_items:]
    return history

def groq_answer(history):
    # history уже содержит user/assistant, system добавляем отдельно
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
        max_tokens=1000,
    )
    return response.choices[0].message.content

# ------------------- HANDLERS -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋 Я твой личный репетитор.\n\n"
        "🎯 Цель — Junior Analyst / BizOps в Coinbase.\n\n"
        "7 модулей, 35+ уроков, домашние задания после каждого урока.\n\n"
        "Выбери с чего начать 👇",
        reply_markup=main_menu_keyboard(),
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "main_menu":
        await query.edit_message_text("Главное меню 👇", reply_markup=main_menu_keyboard())
        return

    if data == "show_modules":
        await query.edit_message_text("📚 Выбери модуль 👇", reply_markup=modules_keyboard())
        return

    if data.startswith("module_"):
        module_id = data.split("_", 1)[1]
        module = MODULES.get(module_id)
        if not module:
            await query.edit_message_text("Такого модуля нет 😅", reply_markup=modules_keyboard())
            return
        await query.edit_message_text(f"{module['name']}\n\nВыбери урок 👇", reply_markup=lessons_keyboard(module_id))
        return

    if data == "reset":
        chat_histories.pop(user_id, None)
        await query.edit_message_text(
            "История очищена! 🔄\n\nВыбери с чего начать 👇",
            reply_markup=main_menu_keyboard(),
        )
        return

    if data.startswith("lesson_"):
        lesson_id = data.split("_", 1)[1]
        history = get_user_history(user_id)

        lesson_prompt = (
            f"Начни урок {lesson_id} по программе. "
            f"Проведи полный урок по структуре и в конце обязательно дай домашнее задание."
        )
        history.append({"role": "user", "content": lesson_prompt})
        chat_histories[user_id] = trim_history(history)

        # короткое служебное сообщение можно редактировать
        try:
            await query.edit_message_text(f"⏳ Загружаю урок {lesson_id}...")
        except Exception:
            pass

        try:
            reply = groq_answer(chat_histories[user_id])
            chat_histories[user_id].append({"role": "assistant", "content": reply})
            chat_histories[user_id] = trim_history(chat_histories[user_id])

            keyboard = [[InlineKeyboardButton("📚 Выбрать другой урок", callback_data="show_modules")]]

            # ВАЖНО: длинные ответы отправляем частями (не edit_message_text)
            await send_long_text(
                context.bot,
                query.message.chat_id,
                reply,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        except Exception as e:
            logging.exception("Ошибка в уроке: %s", e)
            await context.bot.send_message(chat_id=query.message.chat_id, text="Ошибка, попробуй ещё раз 🙏")
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = (update.message.text or "").strip()

    if not user_message:
        return

    history = get_user_history(user_id)
    history.append({"role": "user", "content": user_message})
    chat_histories[user_id] = trim_history(history)

    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        reply = groq_answer(chat_histories[user_id])
        chat_histories[user_id].append({"role": "assistant", "content": reply})
        chat_histories[user_id] = trim_history(chat_histories[user_id])

        keyboard = [[InlineKeyboardButton("📚 Выбрать урок", callback_data="show_modules")]]
        await send_long_text(
            context.bot,
            update.effective_chat.id,
            reply,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    except Exception as e:
        logging.exception("Ошибка в сообщении: %s", e)
        await update.message.reply_text("Ошибка, попробуй ещё раз 🙏")

# ------------------- RUN -------------------
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Бот запущен! ✅")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
  

