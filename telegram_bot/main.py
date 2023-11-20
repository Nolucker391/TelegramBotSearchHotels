import datetime
import telebot.types

from peewee import IntegrityError
from telebot import StateMemoryStorage, TeleBot
from telebot import types
from telebot.custom_filters import StateFilter
from telebot.types import BotCommand, Message
from models import User, create_models
from config import date_base_path, bot_token


state_storage = StateMemoryStorage()

bot = TeleBot(bot_token, state_storage = state_storage)

@bot.message_handler(commands=["start"])
def start_handler(message: Message) -> None:
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    try:
        User.create(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,

        )

        bot.reply_to(message, f"Добро пожаловать в бизнес-приложение {username}!")

    except IntegrityError:
        bot.reply_to(message, f"Рад вас снова видеть, {first_name}!")


    list_for_comands = [
        '/help — помощь по командам бота 🆘',
        "/low — вывод минимальных показателей 📉",
        "/high — вывод максимальных 📈",
        "/custom — вывод показателей пользовательского диапазона 📊",
        "/history — вывод истории запросов пользователей 📝"
    ]

    keyboard = types.InlineKeyboardMarkup()

    for name in list_for_comands:
        keyboard.add(types.InlineKeyboardButton(name, callback_data="button"))

    bot.send_message(message.chat.id, '\tВыберите что вам надо', reply_markup=keyboard)

@bot.message_handler(commands=["/help"])
def button_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    item1 = types.KeyboardButton("/help")

    markup.add(item1)

    bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)

#bot.infinity_polling()
if __name__ == "__main__":
    create_models()
    bot.infinity_polling()


# import telebot
# from telebot import types
# import time
#
# Token = '6739976117:AAHC4mgWcmqS2BHpE-ISGqkAhqHI09_cDh8'
# bot = telebot.TeleBot(Token)
#
#
# @bot.message_handler(commands=['start'])
# def start(m):
#     keyboard = types.InlineKeyboardMarkup()
#
#     for name in ['/help — помощь по командам бота', '/low']:
#         keyboard.add(types.InlineKeyboardButton(name, callback_data="button"))
#
#     #keyboard.add(*[types.InlineKeyboardButton(name, callback_data="button") for name in ['/help — помощь по командам бота', '/low']])
#
#     # button1 = types.InlineKeyboardButton('Кнопка 1', callback_data='button1')
#     # button2 = types.InlineKeyboardButton('Кнопка 2', callback_data='button2')
#     # keyboard = types.InlineKeyboardMarkup([[button1], [button2]])
#
#     msg = bot.send_message(m.chat.id, 'Список возможностей команд бота:', reply_markup=keyboard)
#
#
# # @bot.message_handler(commands=['start'])
# # def start(m):
# #     keyboard = types.InlineKeyboardMarkup()
# #     keyboard.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in ['Поиск', 'Выбрать документ']])
# #     msg = bot.send_message(m.chat.id, 'Здравствуйте, чем я могу помочь?', reply_markup=keyboard)
#
# if __name__ == "__main__":
#     bot.polling(none_stop=True, interval=0)

 # bot.send_message(
    #     message.chat.id,
    #
    #     "Список возможностей команд бота: \n"
    #     "/help — помощь по командам бота \n"
    #     "/low — вывод минимальных показателей \n"
    #     "/high — вывод максимальных \n"
    #     "/custom — вывод показателей пользовательского диапазона \n"
    #     "/history — вывод истории запросов пользователей",
    #
    #     reply_markup=markup
    # )
    #

    # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # markup.add(*[types.KeyboardButton(name) for name in [
    #     "/help — помощь по командам бота\n",
    #     "/low — вывод минимальных показателей\n",
    #     "/high — вывод максимальных",
    #     "/custom — вывод показателей пользовательского диапазона",
    #     "/history — вывод истории запросов пользователей"]])