import logging
from datetime import datetime
import pytz
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
GROUP_ID = -1003998295077
TOPIC_ID = 16  # Тема "Знакомства"

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

NAME, CITY, WORK, VALUE, WHY, INSTAGRAM, RULES = range(7)

RULES_TEXT = (
    "Прежде чем продолжить, познакомься с правилами нашего клуба\n\n"
    "1. Уважительное общение — это основа всего\n"
    "2. Оскорбления и конфликты недопустимы\n"
    "3. Никакой агрессивной рекламы\n"
    "4. Делимся только проверенными рекомендациями\n"
    "5. Всё, что происходит в клубе — остаётся внутри\n"
    "6. Мы здесь для того, чтобы быть полезными друг другу\n\n"
    "Клуб создан для женщин, которые хотят давать и получать — "
    "поддержку, контакты, опыт и тёплое общение."
)


def get_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(GOOGLE_CREDS, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    if not sheet.get_all_values():
        sheet.insert_row(
            ["Дата", "Имя", "Город", "Занятие", "Польза", "Почему", "Instagram", "Username", "Telegram ID", "Статус"],
            index=1
        )
    return sheet


def add_to_sheet(data, username, user_id):
    sheet = get_sheet()
    tz = pytz.timezone("Europe/Berlin")
    row = [
        datetime.now(tz).strftime("%d.%m.%Y %H:%M"),
        data.get("name", ""),
        data.get("city", ""),
        data.get("work", ""),
        data.get("value", ""),
        data.get("why", ""),
        "@" + username if username else "нет",
        str(user_id),
        data.get("instagram", ""),
        "На рассмотрении"
    ]
    sheet.append_row(row)


def update_status(user_id, status):
    try:
        sheet = get_sheet()
        rows = sheet.get_all_values()
        for i, row in enumerate(rows):
            if len(row) >= 8 and row[7] == str(user_id):
                sheet.update_cell(i + 1, 10, status)
                break
    except Exception as e:
        logger.error("Ошибка обновления статуса: %s", e)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Привет!\n\n"
        "Ты сделала первый шаг к вступлению в Девочки Рулят — "
        "закрытый клуб для украинок и русскоязычных женщин в Германии.\n\n"
        "Здесь собираются интересные, активные и открытые женщины, "
        "которые хотят находить своих людей, делиться опытом "
        "и быть полезными друг другу.\n\n"
        "Вход в клуб по анкете — это займёт около 2 минут.\n\n"
        "Начнём? Как тебя зовут?"
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        "Очень приятно, " + update.message.text + "!\n\n"
        "В каком городе Германии ты живёшь или работаешь?"
    )
    return CITY


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text
    await update.message.reply_text(
        "Чем ты занимаешься? Расскажи немного о себе — "
        "работа, бизнес, профессия или, может быть, сейчас в поиске."
    )
    return WORK


async def get_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["work"] = update.message.text
    await update.message.reply_text(
        "Это важный вопрос, который мы задаём всем.\n\n"
        "Чем ты можешь быть полезна участницам клуба?\n\n"
        "Может быть, у тебя есть опыт, знания, контакты или просто "
        "желание поддерживать других — всё это ценно."
    )
    return VALUE


async def get_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["value"] = update.message.text
    await update.message.reply_text(
        "И последний вопрос перед правилами.\n\n"
        "Почему тебе интересно быть в этом клубе?\n\n"
        "Что ты хочешь найти здесь — для себя?"
    )
    return WHY


async def get_why(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["why"] = update.message.text
    await update.message.reply_text(
        "И последнее — есть ли у тебя Instagram?\n\n"
        "Поделись ссылкой на профиль, если хочешь.\n"
        "Если нет — просто напиши нет."
    )
    return INSTAGRAM


async def get_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["instagram"] = update.message.text
    keyboard = [[
        InlineKeyboardButton("Да, принимаю", callback_data="rules_yes"),
        InlineKeyboardButton("Нет", callback_data="rules_no"),
    ]]
    await update.message.reply_text(RULES_TEXT)
    await update.message.reply_text(
        "Ты согласна соблюдать эти правила и быть частью нашего клуба?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return RULES


async def get_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "rules_no":
        await query.edit_message_text(
            "Спасибо за честность.\n\n"
            "Без согласия с правилами мы не сможем принять заявку — "
            "это важно для атмосферы клуба.\n\n"
            "Если передумаешь — просто напиши /start, мы всегда рады."
        )
        return ConversationHandler.END

    user = query.from_user
    d = context.user_data
    username = user.username if user.username else ""

    try:
        add_to_sheet(d, username, user.id)
        logger.info("Заявка записана: %s", d.get("name"))
    except Exception as e:
        logger.error("Ошибка записи в таблицу: %s", e)

    admin_card = (
        "Новая заявка в Девочки Рулят!\n\n"
        "Имя: " + d.get("name", "") + "\n"
        "Город: " + d.get("city", "") + "\n"
        "Занятие: " + d.get("work", "") + "\n"
        "Польза: " + d.get("value", "") + "\n"
        "Почему: " + d.get("why", "") + "\n"
        "Instagram: " + d.get("instagram", "") + "\n\n"
        "ID: " + str(user.id) + "\n"
        "Username: " + ("@" + username if username else "нет")
    )

    group_card = (
        "Новая участница!\n\n"
        "Имя: " + d.get("name", "") + "\n"
        "Город: " + d.get("city", "") + "\n"
        "Занятие: " + d.get("work", "") + "\n"
        "Чем могу быть полезна: " + d.get("value", "") + "\n"
        "Почему хочу в клуб: " + d.get("why", "") + "\n"
        "Instagram: " + d.get("instagram", "") + "\n"
        "Username: " + ("@" + username if username else "нет")
    )

    # Сохраняем визитку для группы
    context.bot_data["group_card_" + str(user.id)] = group_card

    keyboard = [[
        InlineKeyboardButton("Одобрить", callback_data="approve_" + str(user.id)),
        InlineKeyboardButton("Отклонить", callback_data="reject_" + str(user.id)),
    ]]
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_card,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await query.edit_message_text(
        "Твоя заявка отправлена!\n\n"
        "Мы внимательно её рассмотрим и ответим тебе здесь в течение 24-48 часов.\n\n"
        "Если тебя одобрят — твоя анкета будет опубликована в группе, "
        "чтобы участницы могли познакомиться с тобой."
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
        update_status(applicant_id, "Одобрена")
        await context.bot.send_message(
            chat_id=applicant_id,
            text=(
                "Добро пожаловать в Девочки Рулят!\n\n"
                "Твоя заявка одобрена — мы рады, что ты с нами!\n\n"
                "Вот ссылка для вступления в наш клуб:\n" + GROUP_LINK + "\n\n"
                "Когда зайдёшь — твоя анкета будет опубликована в разделе Знакомства, "
                "чтобы все смогли познакомиться с тобой.\n\n"
                "Увидимся внутри!"
            )
        )
        # Публикуем визитку в теме Знакомства
        group_card = context.bot_data.get("group_card_" + str(applicant_id))
        if group_card:
            try:
                await context.bot.send_message(
                    chat_id=GROUP_ID,
                    text=group_card,
                    message_thread_id=TOPIC_ID
                )
            except Exception as e:
                logger.error("Ошибка публикации в группу: %s", e)

        await query.edit_message_text(query.message.text + "\n\nОдобрено — ссылка отправлена")
    else:
        update_status(applicant_id, "Отклонена")
        await context.bot.send_message(
            chat_id=applicant_id,
            text=(
                "Спасибо, что заинтересовалась нашим клубом.\n\n"
                "К сожалению, сейчас мы не можем принять твою заявку.\n\n"
                "Следи за нашим Instagram — возможно, мы снова откроем приём."
            )
        )
        await query.edit_message_text(query.message.text + "\n\nОтклонено")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Анкета сброшена.\n\n"
        "Если захочешь вступить — просто напиши /start, мы всегда рады!"
    )
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
            INSTAGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_instagram)],
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
