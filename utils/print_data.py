import database

from loader import bot
from telebot.types import Message, Dict
from loguru import logger
from utils import find_hotels


def print_data(message: Message, data: Dict) -> None:
    """
    Выводим в чат всё, что собрали от пользователя и передаем это в функцию поиска
    отелей.
    : param message : Message
    : param data: Dict данные собранные от пользователя
    : return : None
    """

    database.add_user_in_database.add_query(data)

    logger.info("Вывод суммарной информации о параметрах запроса пользователем.")

    text_message = (
        "<b><u>Исходные данные:</u></b>\n"
        f'- Дата и время запроса: {data["date_time"]}\n'
        f'- Введена команда: {data["command"]}\n'
        f'- Вы ввели город: <b>{data["input_city"]}</b>\n'
        f'- Количество отелей: {data["quantity_hotels"]}\n'
        f'- Минимальный ценник: {data["price_min"]}\n'
        f'- Максимальный ценник: {data["price_max"]}\n'
        f'- Дата заезда: {data["checkInDate"]["day"]}-'
        f'{data["checkInDate"]["month"]}-{data["checkInDate"]["year"]}\n'
        f'- Дата выезда: {data["checkOutDate"]["day"]}-'
        f'{data["checkOutDate"]["month"]}-{data["checkOutDate"]["year"]}\n'
    )

    if data["sort"] == "DISTANCE":
        bot.send_message(
            message.chat.id,
            text_message + f'• Начало диапазона от центра: {data["landmark_in"]}\n'
            f'• Конец диапазона от центра: {data["landmark_out"]}',
            parse_mode="html",
        )

    else:
        bot.send_message(message.chat.id, text_message, parse_mode="html")

    bot.send_message(
        message.chat.id,
        "<b>Выдаю информации по отелям.</b>\nЕсли процесс долгий, пожалуйста подождите :)",
        parse_mode="html",
    )

    find_hotels.find_and_show_hotels(message, data)
