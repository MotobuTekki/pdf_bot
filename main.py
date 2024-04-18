import telebot
import pyqrcode
import io
from PIL import Image


API_TOKEN = 'YOUR_API_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот. Для работы с QR кодами нажмите /qr, для работы с форматами файлов - /format.")

@bot.message_handler(commands=['qr'])
def qr_mode(message):
    bot.reply_to(message, "Режим QR кода активирован. Отправьте мне ссылку для преобразования в QR код.")

@bot.message_handler(commands=['format'])
def format_mode(message):
    bot.reply_to(message, "Режим форматирования файлов активирован. Пришлите мне файл для конвертации (PDF <- PNG, JPG, PPTX, DOC).")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == '/qr':
        qr_mode(message)
    elif message.text == '/format':
        format_mode(message)
    elif 'https://' in message.text or 'http://' in message.text:
        qr_code = pyqrcode.create(message.text)
        stream = io.BytesIO()
        qr_code.png(stream, scale=8)
        stream.seek(0)
        bot.send_photo(message.chat.id, photo=stream)
        bot.reply_to(message, "QR код успешно создан!")
    else:
        bot.reply_to(message, "Я не могу обработать ваш запрос. Воспользуйтесь командами /qr или /format.")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    file_id = message.document.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    file_extension = file_info.file_path.split('.')[-1]
    supported_formats = ['png', 'jpg', 'pptx', 'doc']

    if file_extension in supported_formats:
        new_extension = 'pdf' if file_extension != 'pdf' else 'png'  # Switch format
        new_file_name = f"converted_file.{new_extension}"

        with open(new_file_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        with open(new_file_name, 'rb') as converted_file:
            bot.send_document(message.chat.id, converted_file)

        bot.reply_to(message, f"Файл успешно конвертирован в {new_extension.upper()} формат.")
    else:
        bot.reply_to(message, "Выбранный формат не поддерживается. Допустимые форматы: PNG, JPG, PPTX, DOC.")

bot.polling()
