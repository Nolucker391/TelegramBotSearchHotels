from loader import bot
from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS

@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    """
    Функция help (помощи) отправляет пользователю:

    - информацию об боте
    - список команд

    """

    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]

    bot.reply_to(message, "Данный телеграмм бот позволяет найти выгодное предложение на платформе Hotels.com в нужном вам городе."
                          "\nНиже приведен список основных функций бота ⬇⬇")

    transcription = "__" * 16

    bot.send_message(chat_id=message.chat.id, text=f"\n<b>{transcription}</b>\n".join(text), parse_mode="html")