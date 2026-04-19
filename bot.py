import logging
import json
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8762973970:AAHVP0OLco-jDU8a-q6WqfEb15WRMHxQYyw"
ADMIN_ID = 691846456
GROUP_LINK = "https://t.me/+tLpqhb4CvOYyMjk6"
SHEET_ID = "1DfHKP3uXaEy4ZaKZRAeghPGlvLX7BWwnl6cVg7gyKPc"

NAME, CITY, WORK, VALUE, WHY, RULES = range(6)

RULES_TEXT = """📋 Правила нашего клуба:

1. Уважительное общение со всеми участницами
2. Оскорбления и конфликты — недопустимы
3. Никакой агрессивной рекламы
4. Делимся только проверенными рекомендациями
5. Всё, что обсуждается в клубе — остаётся внутри
6. Наша цель — поддержка и польза друг другу"""


def get_sheet():
    creds_json = os.environ.get("GOOGLE_CREDS_JSON")
    creds_dict = json.loads(creds_json)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    if not sheet.get_all_values():
        sheet.insert_row(
            ["Дата", "Имя", "Город", "Занятие", "Польза", "Почему", "Username", "Telegram ID", "Статус"],
            index=1
        )
    return sheet


def add_to_sheet(data: dict, username: str, user_id: int):
    sheet = get_sheet()
    row = [
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        data.get("name", ""),
        data.get("city", ""),
        data.get("work", ""),
        data.get("value", ""),
        data.get("why", ""),
        f"@{username}" if username else "нет",
        str(user_id),
        "На рассмотрении"
    ]
    sheet.append_row(row)


def update_status(user_id: int, status: str):
    try:
        sheet = get_sheet()
        rows = sheet.get_all_values()
        for i, row in enumerate(rows):
            if len(row) >= 8 and row[7] == str(user_id):
                sheet.update_cell(i + 1, 9, status)
                break
    except Exception as e:
        logger.error(f"Ошибка обновления статуса: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Привет! 👋\n\n"
        "Я помогу тебе подать заявку в закрытый Женский клуб Дюссельдорфа 🌸\n\n"
        "Это русскоязычное сообщество, где женщины помогают друг другу, "
        "находят хороших мастеров и просто общаются.\n\n"
        "Анкета займёт 2 минуты ⏱\n\n"
        "Как тебя зовут? 😊"
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("В каком городе Германии ты живёшь? 📍")
    return CITY


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text
    await update.message.reply_text("Чем ты занимаешься? (работа / бизнес / в поиске) 💼")
    return WORK


async def get_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["work"] = update.message.text
    await update.message.reply_text("Чем ты можешь быть полезна участницам клуба? 🤝")
    return VALUE


async def get_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["value"] = update.message.text
    await update.message.reply_text("Почему тебе интересно быть в этом клубе? 💛")
    return WHY


async def get_why(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["why"] = update.message.text
    keyboard = [[
        InlineKeyboardButton("✅ Да, согласна", callback_data="rules_yes"),
        InlineKeyboardButton("❌ Нет", callback_data="rules_no"),
    ]]
    await update.message.reply_text(RULES_TEXT)
    await update.message.reply_text(
        "Ты согласна соблюдать эти правила? 🤝",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return RULES


async def get_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "rules_no":
        await query.edit_message_text(
            "Спасибо за честность 🙏\n\n"
            "Без согласия с правилами мы не сможем принять заявку.\n"
            "Если передумаешь — просто напиши /start 💛"
        )
        return ConversationHandler.END

    user = query.from_user
    d = context.user_data
    username = user.username if user.username else ""

    try:
        add_to_sheet(d, username, user.id)
        logger.info(f"Заявка записана в таблицу: {d.get('name')}")
    except Exception as e:
        logger.error(f"Ошибка записи в таблицу: {e}")

    card = (
        f"🔔 Новая заявка в клуб!\n\n"
        f"👤 Имя: {d.get('name', '')}\n"
        f"📍 Город: {d.get('city', '')}\n"
        f"💼 Занятие: {d.get('work', '')}\n"
        f"🤝 Польза: {d.get('value', '')}\n"
        f"💛 Почему: {d.get('why', '')}\n\n"
        f"ID: {user.id}\n"
        f"Username: {'@' + username if username else 'нет'}"
    )
    keyboard = [[
        InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{user.id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user.id}"),
    ]]
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=card,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await query.edit_message_text(
        "Спасибо! 🙏\n\n"
        "Твоя заявка отправлена на рассмотрение.\n\n"
        "Мы рассмотрим её в течение 24-48 часов и ответим тебе здесь 💛"
    )
    return ConversationHandler.END


async def handle_admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    action, applicant_id = query.data.split("_", 1)
    applicant_id = int(applicant_id)

    if action == "approve":
        update_status(applicant_id, "✅ Одобрена")
        await context.bot.send_message(
            chat_id=applicant_id,
            text=(
                "🎉 Поздравляем! Твоя заявка одобрена!\n\n"
                "Добро пожаловать в Женский клуб Дюссельдорфа 🌸\n\n"
                f"Вот ссылка для вступления:\n{GROUP_LINK}"
            )
        )
        await query.edit_message_text(query.message.text + "\n\n✅ Одобрено — ссылка отправлена")
    else:
        update_status(applicant_id, "❌ Отклонена")
        await context.bot.send_message(
            chat_id=applicant_id,
            text=(
                "Спасибо за интерес к нашему клубу 🙏\n\n"
                "К сожалению, сейчас мы не можем принять твою заявку.\n\n"
                "Следи за нашим Instagram 💛"
            )
        )
        await query.edit_message_text(query.message.text + "\n\n❌ Отклонено")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Анкета сброшена. Напиши /start чтобы начать заново 💛")
    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CITY:  [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            WORK:  [MessageHandler(filters.TEXT & ~filters.COMMAND, get_work)],
            VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_value)],
            WHY:   [MessageHandler(filters.TEXT & ~filters.COMMAND, get_why)],
            RULES: [CallbackQueryHandler(get_rules, pattern="^rules_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(handle_admin_decision, pattern="^(approve|reject)_"))
    logger.info("Бот запущен!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
