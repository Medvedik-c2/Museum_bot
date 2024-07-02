import logging
import os
import psycopg2
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# Подключение к базе данных
def connect_db():
    return psycopg2.connect(
        dbname="museum",
        user="your_username",
        password="your_password",
        host="localhost",
        port="5432"
    )


# Обработчик команды /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Отправь номер экспоната, чтобы получить аудиозапись с его описанием.')


# Обработчик текстовых сообщений
def handle_message(update: Update, context: CallbackContext) -> None:
    try:
        number = int(update.message.text)
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT description, audio_path FROM exhibits WHERE number = %s", (number,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            description, audio_path = result
            update.message.reply_text(description)
            audio_file = InputFile(audio_path)
            update.message.reply_audio(audio_file)
        else:
            update.message.reply_text('Экспонат с таким номером не найден.')

    except ValueError:
        update.message.reply_text('Пожалуйста, отправьте правильный номер экспоната.')

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        update.message.reply_text('Произошла ошибка при обработке запроса.')


def main() -> None:
    # Получение токена бота
    token = 'YOUR_TELEGRAM_BOT_TOKEN'

    updater = Updater(token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
