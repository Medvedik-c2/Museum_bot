import logging
import os
import psycopg2
import time
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, UpdaterDataHandler

# Настройка логирования
logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level=logging.INFO
)

logger = logging.getLogger(__name__)

# Подключение к базе данных
def connect_db():
  return psycopg2.connect(
    dbname=os.getenv('DB_NAME', 'museum'),
    user=os.getenv('DB_USER', 'your_username'),
    password=os.getenv('DB_PASSWORD', 'your_password'),
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432')
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

# Функция отправки запроса отзыва
def send_feedback_request(update: Update, context: CallbackContext) -> None:
    delay = 20 * 60  # 20 минут в секундах
    last_request_time = context.user_data.get('last_request_time')

    if time.time() - last_request_time > delay:
        update.message.reply_text('Понравился ли вам наш музей и аудиогид? Пожалуйста, оставьте отзыв!')
        context.user_data['last_request_time'] = time.time()

# Обработка отзыва
def handle_feedback(update: Update, context: CallbackContext) -> None:
    # Сохранение отзыва
    feedback = update.message.text
    # ... (Запись отзыва в журнал) ...

    # Отправка благодарности
    update.message.reply_text('Спасибо за ваш отзыв!')

    # Сброс состояния пользователя
    context.user_data['waiting_for_feedback'] = False

# Обновление контекста пользователя
def update_user_data(update: Update, context: CallbackContext) -> None:
    if update.message is not None:
        context.user_data['last_request_time'] = time.time()
        context.user_data['waiting_for_feedback'] = False

def main() -> None:
  # Получение токена бота
  token = os.getenv('TELEGRAM_BOT_TOKEN')
   
  updater = Updater(token)
   
  dispatcher = updater.dispatcher

  dispatcher.add_handler(CommandHandler("start", start))
  dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
  dispatcher.add_handler(MessageHandler(Filters.text & context.user_data.get('waiting_for_feedback', False), handle_feedback))

  updater.user_data_handler = UpdaterDataHandler(update_user_data)

  updater.start_polling()
  updater.idle()

if __name__ == '__main__':
  main()
