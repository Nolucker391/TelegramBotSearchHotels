import sqlite3
import database

from telebot.types import Message
from loader import bot


@bot.message_handler(commands=["start"])
def bot_start(message: Message) -> None:
    """
        Функция start (стартовое окно) отправляет пользователю:
        - приветствие
        - если пользователь новый - информацию с приветствием

    : param user_id : int
    : param username : str
    : param first_name : str
    : param last_name : str
    : return : None

    """

    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    with sqlite3.connect("database/history.db") as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT chat_id FROM user WHERE chat_id = ?", (user_id,))
        records = cursor.fetchall()

        try:

            if records != [] and records[0][0] == user_id:
                bot.reply_to(
                    message,
                    text=f"Рад вас снова видеть, <b>{first_name}</b>{last_name}!",
                    parse_mode="html",
                )

            else:
                bot.reply_to(
                    message,
                    text=f"Привет, <b>{first_name}</b>{last_name}!\n"
                    f"Добро пожаловать в приложение - для поиска отелей 🏩"
                    f"\nВоспользуйтесь командой <b><u>/help</u></b> - для получения информации.",
                    parse_mode="html",
                )
                database.add_user_in_database.add_user(
                    message.chat.id,
                    message.from_user.username,
                    message.from_user.full_name,
                )
        except sqlite3.IntegrityError:
            pass
