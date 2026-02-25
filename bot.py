import os
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

SYSTEM_PROMPT = """
Ты — личный репетитор по бизнесу, аналитике и финтеху. Твоя главная цель — подготовить ученика 18 лет к роли Junior Analyst / BizOps в Coinbase или аналогичной крипто/tech компании.
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
═══════════════════════════════
ПРОГРАММА ОБУЧЕНИЯ (6 модулей)
═══════════════════════════════

МОДУЛЬ 1 — Как работает бизнес
  Урок 1.1: Как устроена компания (структура, роли, отделы)
  Урок 1.2: Как компании зарабатывают деньги (бизнес-модели)
  Урок 1.3: Юнит-экономика — считаем прибыль на одного клиента
  Урок 1.4: P&L — отчёт о прибылях и убытках
  Урок 1.5: Как читать финансовую отчётность

МОДУЛЬ 2 — Аналитика и метрики
  Урок 2.1: Основные бизнес-метрики (MAU, DAU, Churn, LTV, CAC)
  Урок 2.2: Воронка продаж и конверсия
  Урок 2.3: SQL — основы (SELECT, WHERE, GROUP BY)
  Урок 2.4: SQL — продвинутый (JOIN, подзапросы, оконные функции)
  Урок 2.5: Excel / Google Sheets для аналитика
  Урок 2.6: Как строить дашборды и презентовать данные

МОДУЛЬ 3 — Финтех и крипто
  Урок 3.1: Как работают традиционные финансы (банки, платежи)
  Урок 3.2: Что такое блокчейн и крипто (простым языком)
  Урок 3.3: Как работает Coinbase — бизнес-модель, продукты, выручка
  Урок 3.4: DeFi — децентрализованные финансы
  Урок 3.5: Регуляции в крипто — что важно знать аналитику
  Урок 3.6: Крипто-метрики (TVL, trading volume, active wallets)

МОДУЛЬ 4 — Продуктовое мышление
  Урок 4.1: Что такое продукт и как его строят
  Урок 4.2: Product metrics — как измерить успех продукта
  Урок 4.3: A/B тесты — как принимают решения в tech
  Урок 4.4: User journey и боли пользователя
  Урок 4.5: Как писать PRD (Product Requirements Document)

МОДУЛЬ 5 — BizOps на практике
  Урок 5.1: Что делает BizOps каждый день
  Урок 5.2: Как приоритизировать задачи (frameworks: RICE, MoSCoW)
  Урок 5.3: Процессы и операционная эффективность
  Урок 5.4: Работа с данными для принятия решений
  Урок 5.5: Стейкхолдеры — как работать с разными командами

МОДУЛЬ 6 — Подготовка к Coinbase
  Урок 6.1: Как устроен процесс найма в Coinbase
  Урок 6.2: Типичные вопросы на интервью (behavioural)
  Урок 6.3: Бизнес-кейсы — как решать и презентовать
  Урок 6.4: SQL задачи с реальных интервью
  Урок 6.5: Как написать резюме и cover letter для Coinbase
  Урок 6.6: Финальный mock-интервью

═══════════════════════════════
КАК ВЕСТИ УРОКИ
═══════════════════════════════

1) Начинай каждый урок с приветствия и названия темы
2) Объясняй по структуре:
   🔷 Что это
   🔷 Зачем нужно (особенно для Coinbase/крипто)
   🔷 Пример из реальной жизни
   🔷 Типичная ошибка новичка
   🔷 Мини-вопрос на проверку
3) Не переходи к следующей теме пока ученик не ответил правильно
4) Если ошибся — мягко объясни и дай ещё шанс
5) В конце каждого урока давай мини-задание
6) Всегда связывай материал с реальной работой в Coinbase

═══════════════════════════════
ПРАВИЛА ОБЩЕНИЯ
═══════════════════════════════

- Простые слова, без жаргона (или объясняй термин сразу)
- Коротко и по делу — не пиши стены текста
- Дружелюбно и мотивирующе
- Если пишет "не понял" — объясни через аналогию из жизни
- Отвечай на том же языке на котором пишет ученик
- Периодически напоминай что цель — Coinbase 🎯

═══════════════════════════════
КОМАНДЫ
═══════════════════════════════

/start — приветствие и старт программы
/program — показать всю программу обучения
/lesson [номер] — начать конкретный урок (например /lesson 1.1)
/progress — показать прогресс ученика
/reset — начать заново
"""

client = Groq(api_key=GROQ_API_KEY)
chat_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋 Я твой личный репетитор.\n\n"
        "🎯 Наша цель — подготовить тебя к роли Junior Analyst / BizOps в Coinbase.\n\n"
        "У нас 6 модулей и 30+ уроков — от основ бизнеса до реального интервью.\n\n"
        "Напиши /program чтобы увидеть всю программу\n"
        "Или просто напиши 'начнём' — и стартуем с первого урока! 🚀"
    )

async def program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 ПРОГРАММА ПОДГОТОВКИ К COINBASE\n\n"
        "Модуль 1 — Как работает бизнес (5 уроков)\n"
        "Модуль 2 — Аналитика и метрики + SQL (6 уроков)\n"
        "Модуль 3 — Финтех и крипто (6 уроков)\n"
        "Модуль 4 — Продуктовое мышление (5 уроков)\n"
        "Модуль 5 — BizOps на практике (5 уроков)\n"
        "Модуль 6 — Подготовка к интервью Coinbase (6 уроков)\n\n"
        "Напиши /lesson 1.1 чтобы начать первый урок\n"
        "Или просто напиши 'начнём' 🚀"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    if user_id not in chat_histories:
        chat_histories[user_id] = []

    chat_histories[user_id].append({
        "role": "user",
        "content": user_message
    })

    if len(chat_histories[user_id]) > 30:
        chat_histories[user_id] = chat_histories[user_id][-30:]

    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + chat_histories[user_id],
            max_tokens=1000,
        )

        reply = response.choices[0].message.content

        chat_histories[user_id].append({
            "role": "assistant",
            "content": reply
        })

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("Ошибка, попробуй ещё раз 🙏")
        print(f"Ошибка: {e}")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in chat_histories:
        del chat_histories[user_id]
    await update.message.reply_text("История очищена! Начинаем заново 🔄")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("program", program))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Бот запущен! ✅")
app.run_polling()
