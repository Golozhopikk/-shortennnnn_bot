from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from transformers import pipeline

# Создаем модели для суммаризации
weak_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
strong_summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Привет! Я могу сжать ваш текст на двух уровнях:\n"
        "1. Сильное сжатие (одно-два предложения)\n"
        "2. Слабое сжатие (краткий абзац)\n\n"
        "Отправьте мне текст, и выберите уровень сжатия."
    )

async def handle_text(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    context.user_data['text'] = text  # Сохраняем текст пользователя

    # Создаем кнопки для выбора уровня сжатия
    keyboard = [
        [
            InlineKeyboardButton("Сильное сжатие", callback_data='strong'),
            InlineKeyboardButton("Слабое сжатие", callback_data='weak'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите уровень сжатия:', reply_markup=reply_markup)

async def summarize(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    compression_level = query.data
    text = context.user_data.get('text')

    if not text:
        await query.edit_message_text(text="Произошла ошибка. Пожалуйста, отправьте текст снова.")
        return

    if compression_level == 'strong':
        summary = strong_summarizer(text, max_length=45, min_length=15, do_sample=False)
    else:
        summary = weak_summarizer(text, max_length=100, min_length=50, do_sample=False)

    summarized_text = summary[0]['summary_text']
    await query.edit_message_text(text=f"📝 Результат:\n\n{summarized_text}")

def main() -> None:
    # Используем ApplicationBuilder вместо Updater
    application = ApplicationBuilder().token("7705332084:AAEne2FzfkpGeaak3DNXY4fnUgSm_5ogDd0").build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(summarize))

    application.run_polling()

if __name__ == '__main__':
    main()