import telebot

API_TOKEN = '6961515410:AAHNhBjTn0ajhwUs-0qsya1z4F6tnM2nE2w'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Здравствуйте! Перейдите по ссылке для бронирования билета: http://your-web-app-url.com")

bot.infinity_polling()
