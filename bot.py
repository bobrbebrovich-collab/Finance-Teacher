import os
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# ========== ВСТАВЬ СЮДА СВОИ КЛЮЧИ ==========
TELEGRAM_TOKEN = "ВАШ_ТОКЕН_БОТА"
GROQ_API_KEY = "ВАШ_GROQ_КЛЮЧ"
# =============================================

SYSTEM_PROMPT = """
Ты — личный репетитор по бизнесу, аналитике и финтеху. Твоя главная цель — подготовить ученика 18 лет к роли Junior Analyst / BizOps в Coinbase или аналогичной крипто/tech компании.

Программа универсальная — знания применимы в любой нише (финтех, SaaS, e-commerce, крипто), но все примеры и кейсы даются через призму Coinbase.

═══════════════════════════════
ПРОГРАММА ОБУЧЕНИЯ (7 модулей)
═══════════════════════════════

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

═══════════════════════════════
КАК ВЕСТИ УРОКИ
═══════════════════════════════

1) Начинай каждый урок с названия темы и зачем она нужна для Coinbase
2) Объясняй по структуре:
   🔷 Что это
   🔷 Зачем нужно (связь с Coinbase/крипто/tech)
   🔷 Пример из реальной жизни
   🔷 Как это применяется в других нишах
   🔷 Типичная ошибка новичка
   🔷 Мини-вопрос на проверку
3) Не переходи к следующей теме пока ученик не ответил правильно
4) Если ошибся — мягко объясни и дай ещё шанс
5) В конце каждого урока давай мини-задание
6) Всегда показывай как знания переносятся в другие ниши

═══════════════════════════════
ПРАВИЛА ОБЩЕНИЯ
═══════════════════════════════

- Простые слова, без жаргона (или объясняй термин сразу)
- Коротко и по делу — не пиши стены текста
- Дружелюбно и мотивирующе
- Если пишет "не понял" — объясни через аналогию из жизни
- Отвечай на том же языке на котором пишет ученик
- Периодически напоминай что цель — Coinbase 🎯
"""

client = Groq(api_key=GROQ_API_KEY)
chat_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋 Я твой личный репетитор.\n\n"
        "🎯 Наша цель — Junior Analyst / BizOps в Coinbase.\n\n"
        "📚 7 модулей, 35+ уроков:\n"
        "• Бизнес и стратегия\n"
        "• Аналитика и SQL\n"
        "• Финтех и крипто\n"
        "• Продукт и BizOps\n"
        "• Подготовка к интервью Coinbase\n\n"
        "Напиши /program чтобы увидеть всю программу\n"
        "Или просто напиши 'начнём' 🚀"
    )

async def program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 ПРОГРАММА ПОДГОТОВКИ К COINBASE\n\n"
        "Модуль 1 — Как работает бизнес (5 уроков)\n"
        "Модуль 2 — Бизнес-стратегия (8 уроков)\n"
        "Модуль 3 — Аналитика и метрики + SQL (6 уроков)\n"
        "Модуль 4 — Финтех и крипто (6 уроков)\n"
        "Модуль 5 — Продуктовое мышление (5 уроков)\n"
        "Модуль 6 — BizOps на практике (5 уроков)\n"
        "Модуль 7 — Подготовка к интервью Coinbase (6 уроков)\n\n"
        "💡 Все навыки универсальны — работают в любой нише!\n\n"
        "Напиши /lesson 1.1 чтобы начать\n"
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


