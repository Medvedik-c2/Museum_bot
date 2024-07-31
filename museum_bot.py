import telebot

# Токен бота, полученный от BotFather
TOKEN = '****'

# Путь к текстовому файлу с экспонатами
EXHIBITS_FILE = 'exhibits.txt'

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Загрузка списка экспонатов из файла
def load_exhibits():
    exhibits = {}
    with open(EXHIBITS_FILE, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(' ')
            if len(parts) >= 2:
                exhibit_num = parts[0]
                audio_file = parts[1]
                exhibits[exhibit_num] = audio_file
    return exhibits

# Обработчик команды /start или /help
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    bot.send_message(message.chat.id, "Привет! Я бот-аудиогид. Чтобы получить аудиозапись, отправь номер экспоната.")

# Обработчик текстовых сообщений с номером экспоната
@bot.message_handler(func=lambda message: True)
def handle_exhibit_request(message):
    try:
        exhibit_num = message.text.strip()
        exhibits = load_exhibits()
        if exhibit_num in exhibits:
            audio_file = exhibits[exhibit_num]
            audio_path = open(f'{audio_file}', 'rb')
            bot.send_audio(message.chat.id, audio_path)
        else:
            bot.send_message(message.chat.id, "Экспонат не найден.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")


if __name__ == '__main__':
    bot.polling(none_stop=True)
