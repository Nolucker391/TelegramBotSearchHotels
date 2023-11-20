#Сначала мы импортируем библиотеку.

import telebot
from telebot import types

token=("6388000975:AAEqoZUAj31IR5s7mLCiSuBZy-ndlsDZtys")
bot = telebot.TeleBot(token)

@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id, "Дарова")

@bot.message_handler(commands=['button'])
def button_message(message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

	item1 = types.KeyboardButton("Кнопка")
	item2 = types.KeyboardButton("Кнопка 2")

	markup.add(item1,item2)

	bot.send_message(message.chat.id,'Выберите что вам надо',reply_markup=markup)
@bot.message_handler(content_types='text')
def message_reply(message):
	# bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)

	if message.text == "Кнопка":
		bot.send_message(message.chat.id, "Я ИИ")
	elif message.text == "Кнопка 2":
		bot.send_message(message.chat.id, "Я НЕ ИИ")
	else:
		bot.send_message(message.chat.id, "Не понимаю")
	# elif message.text == "Кнопка 2":
	# 	bot.send_message(message.chat.id, 'Спасибо за прочтение статьи!')


if __name__ == "__main__":
	create_models()
	bot.infinity_polling()