import logging
import json
import os
import tempfile
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

GOOGLE_CREDS = {
    "type": "service_account",
    "project_id": "women-club-bot",
    "private_key_id": "f02e40f804bb801528290c7e2509b219bda303b6",
    "private_key": (
        "-----BEGIN PRIVATE KEY-----\n"
        "MIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQDKByBCmRwE5cHA\n"
        "ZY+Qj2P02+Yqo24VgUZDQc+azAOIoRCsZfeo+qnmzuQPCg1zb7z3lbJPNKtOkPM9\n"
        "8WWXfFpi6WSmE6nwUlV/MJ4BVsRsPB+kKcWkrsjHtd8xVVinOR50Su4j9/g0oDPC\n"
        "xhIP4ZHZY3VocRelaAdWx3bvaBTA11PNTGabSTtjEOFwozfIcc9kT4g8F2kWMFGj\n"
        "p7ndlwFteQqk7PR9XffrzGmiUcWvUwg6nSLpFLc4OW/194mvITxOHKKpGmVDP7CT\n"
        "1PhtodV5HZZ9oW+sEgB58yJ8s/z6VH616UZ6t064iJPWLeLvzaY11gOFRO38P5tx\n"
        "PB0wNt+JAgMBAAECggEAHEjuH9Te4uKmA0FU3cjtljEZYvvZpEIiq7Txk3sfvYfL\n"
        "VU+7Ylmh4vIxZNej9Xb97m3zdnppx4isvY3oCtL6tqF1mXjkUIS+ep28aXST8JFk\n"
        "XrAIf1uHOcrBUl9gF518IY0CFWAYzIlnZcwkaDvNFzIBFJvM0zgi2uf3Q2J/kVX0\n"
        "iNZ+lFpS3lNTc4TQFbbdtjT291JZy/OtffXeas7fWGGfSYSh+zGWNibgA9hehbuD\n"
        "wr4uxYQOrm2nranL0fr7nx+l+wkwKGuls9OlgH1unbGCNGJ2qu3IjLWB4yZrRRDL\n"
        "KyViiIHMjMJcDMPO0Bokvd+VwyUCB8MfvS0+hB0aeQKBgQD0lAPCkkbFj0GL99ps\n"
        "HGYUre0Tr/yncv/evNoH5dA5CwRXIIA0qmRa1R6oYKgaZ3ohjWzwFOm0lYD+PM4/\n"
        "FEOf+3dI+/KQVGY3vLxIhO2ReylXDi3AiwvnRrsaAth1QHYFIvh4+DPWzvL61Zcl\n"
        "ufheIsj0F0kEs5+T8lI2wwI53QKBgQDTdmmmM6Tj4FTtWhYpFPBOKfiRhx2OnPfa\n"
        "vjLIHag6QMDLetRNNtQh0Wnh74b6h2Otg/Bq+Qd5QShLPWHGtkwX5ANp3g9tbvk4\n"
        "IEFmCfaYhtR1STzUmistvCcC3Rc2GpkQ723OMkbW2xe3aQYhFQ0oC1dlpjzUoT8T\n"
        "TZ05dkw/nQJ/awBWpMlaLRR/mLzW0nWaM3HkRri30Ip/ZvM4cDwa3Nn1DCkr7d6e\n"
        "CR80SnX/FY4v4H3/Kwn7NQYzaQcxNGepLlTV2xhfBsXl8nyf4xpE1WEMtQl++r3a\n"
        "d1R6hua3zJRnDdg+3K26AECKDTNk7RxvjL+rKx8E0wnCxvc9ALhQQQKBgGiF3U7j\n"
        "tBtXJWN05gNEcEuSf2UfjkKR4AllfiBgWGkC3Mk3W30XHt/gbR/aj7OB/Ikl8E5P\n"
        "7ZvH0yztmEjqjs44TF+l/aYv9kwB1ZGkVxmpe5bFrqW/1pvypq3JrtF1cDdowbPs\n"
        "Mgu9nAlyhi8QAsLKaFa8RtErKsxVzuM6UBIZAoGBAMA2E4A+/zbT7Rtitj1IJMBM\n"
        "y5gtBRFoplWtfadw6WUr+I0ieqaXZzZ3AaZQtbDc9bkI4I6xLxcZ++7xgN6ITRhL\n"
        "w0k0GFgsxgyVZ1zIweI2WVhRLll5Q4WGt71av+4BZx8jFh6LaEnszkOJAQ3FgTzL\n"
        "pvqKLegPSTnsoqKgqB6m\n"
        "-----END PRIVATE KEY-----\n"
    ),
    "client_email": "women-club-bot@women-club-bot.iam.gserviceaccount.com",
    "client_id": "103045299427313456408",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/women-club-bot%40women-club-bot.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

NAME, CITY, WORK, VALUE, WHY, RULES = range(6)

RULES_TEXT = """📋 Правила нашего клуба:

1. Уважительное общение со всеми участницами
2. Оскорбления и конфликты — недопустимы
3. Никакой агрессивной рекламы
4. Делимся только проверенными рекомендациями
5. Всё, что обсуждается в клубе — остаётся внутри
6. Наша цель — поддержка и польза друг другу"""


def get_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(GOOGLE_CREDS, scopes=scopes)
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
