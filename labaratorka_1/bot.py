import telebot
from logger import log_call
from telebot import types
import requests
from secretik import secret


TELEGRAM_TOKEN = secret['BOT_API_TOKEN']

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
@log_call
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cats_btn = types.KeyboardButton("Случайный факт о кошках")
    ip_btn = types.KeyboardButton("Получить мой IP")
    universitets_btn = types.KeyboardButton("Университеты в Беларуси")
    markup.add(cats_btn, ip_btn, universitets_btn)
    bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=markup)
    return ["start"]

@bot.message_handler(func=lambda message: message.text == 'Университеты в Беларуси')
@log_call
def send_universitets(message):
    url = "http://universities.hipolabs.com/search?country=Belarus"
    try:
        response = requests.get(url)
        data = response.json()
        if not data:
            bot.send_message(message.chat.id, "Не удалось найти университеты.")
            return
        reply = "10 университетов в Беларуси:\n\n"
        reply += f"• Academy of National Security\n"
        for uni in data[:9]:
            reply += f"• {uni['name']}\n"
        bot.send_message(message.chat.id, reply)
        return ["send_universities", url, "success"]
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при получении данных: {e}")
        return ["send_universities", url, f"error: {str(e)}"]

@bot.message_handler(func=lambda message: message.text == 'Случайный факт о кошках')
@log_call
def send_cats(message):
    url = "https://catfact.ninja/fact"
    try:
        response = requests.get(url)
        data = response.json()
        if not data:
            bot.send_message(message.chat.id, "Не удалось найти факт.")
            return
        reply = f"Интересный фактик:\n\n• {data['fact']}"
        bot.send_message(message.chat.id, reply)
        return ["send_cats", url, "success"]
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при получении данных: {e}")
        return ["send_cats", url, f"error: {str(e)}"]

@bot.message_handler(func=lambda message: message.text == 'Получить мой IP')
@log_call
def send_ip(message):
    url = "https://api.ipify.org?format=json"
    try:
        response = requests.get(url)
        data = response.json()
        if not data:
            bot.send_message(message.chat.id, "Не удалось найти IP.")
            return
        reply = f"Ваш IP адрес:\n\n• {data['ip']}"
        bot.send_message(message.chat.id, reply)
        return ["send_ip", url, "success"]
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при получении данных: {e}")
        return ["send_ip", url, f"error: {str(e)}"]

@bot.message_handler(func=lambda message: True)
@log_call
def echo_all(message):
    bot.reply_to(message, f"Вы написали: {message.text}, я не знаю такой команды")
    return ["Keyboard typing", "NONE", "NONE"]

def main():
    print("Бот запустился")
    bot.polling()

if __name__ == "__main__":
    main()
