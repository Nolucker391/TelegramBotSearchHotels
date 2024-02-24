from telebot.types import Message
from loader import bot


@bot.message_handler(func=lambda message: True)
def bot_echo(message: Message) -> None:
    """
    Данная функция эхо-ответчик:
    - отвечает пользователю ту же сообщение, что и написал пользователь

    """
    if message.text.lower() == "привет":
        bot.reply_to(message, f"И вам {message.from_user.full_name} - привет!")
    else:
        bot.reply_to(message, f"{message.text}")
