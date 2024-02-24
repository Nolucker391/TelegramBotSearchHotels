import database

from loader import bot
from telebot.types import Message, InputMediaPhoto
from loguru import logger
from states.user_states import User_input_state


@bot.message_handler(commands=["history"])
def history(message: Message) -> None:
    """
    Обработчик команд, срабатывает на команду /history
    Обращается к базе данных и выдает в чат запросы пользователя
    по отелям.
    : param message : Message
    : return : None
    """

    logger.info("Выбрана команда history!")
    queries = database.read_from_database.read_query(message.chat.id)
    logger.info(f"Получены записи из таблицы query:\n {queries}")

    bot.send_message(
        message.chat.id,
        "<u>Раздел /history (История запросов)</u>. <b>Текущий список:</b> ",
        parse_mode="html",
    )

    for item in queries:
        bot.send_message(
            message.chat.id,
            f"<b>№{item[0]}</b>\n- Дата и время: \t{item[1]}. \n- Вы вводили город: {item[2]}",
            parse_mode="html",
        )

    bot.set_state(message.chat.id, User_input_state.history_select)

    bot.send_message(
        message.from_user.id,
        "<b>Введите номер интересующего вас варианта: </b>",
        parse_mode="html",
    )


@bot.message_handler(state=User_input_state.history_select)
def input_city(message: Message) -> None:
    """
    Ввод пользователем номера запроса, которые есть в списке. Если пользователь введет
    неправильный номер или это будет "не цифры", то бот попросит повторить ввод.
    Запрос к базе данных нужных нам записей. Выдача в чат результата.
    : param message : Message
    : return : None
    """

    if message.text.isdigit():

        queries = database.read_from_database.read_query(message.chat.id)
        number_query = []
        photo_need = ""

        for item in queries:
            number_query.append(item[0])

            if int(message.text) == item[0] and item[3] == "yes":
                photo_need = "yes"

        if photo_need != "yes":
            bot.send_message(
                message.chat.id,
                '<b>Вы выбирали вариант вывода - "<u>без фото</u>".</b>',
                parse_mode="html",
            )

        if int(message.text) in number_query:
            history_dict = database.read_from_database.get_history_response(
                message.text
            )
            logger.info("Выдаем результаты выборки из базы данных")

            for hotel in history_dict.items():
                medias = []
                caption = (
                    f"<b>Название отеля:</b> {hotel[1]['name']}\n<b>Адрес отеля:</b> {hotel[1]['address']}"
                    f"\n<b>Стоимость проживания в "
                    f"сутки :</b> {round(hotel[1]['price'], 2)} $\n<b>Расстояние до центра:</b> {hotel[1]['distance']} mile"
                    f"\n<b>Общая стоимость :</b> {hotel[1]['total']}"
                )
                urls = hotel[1]["images"]

                if photo_need == "yes":
                    for number, url in enumerate(urls):
                        if number == 0:
                            medias.append(
                                InputMediaPhoto(
                                    media=url, caption=caption, parse_mode="html"
                                )
                            )
                        else:
                            medias.append(InputMediaPhoto(media=url))

                    bot.send_media_group(message.chat.id, medias)

                else:
                    bot.send_message(message.chat.id, text=caption, parse_mode="html")

            bot.send_message(
                message.chat.id, "<b>Поиск окончен!</b>", parse_mode="html"
            )

            bot.delete_state(message.from_user.id, message.chat.id)
        else:
            bot.send_message(
                message.chat.id,
                "Ошибка! Вы ввели число, которого нет в списке! Повторите ввод!",
            )

    else:
        bot.send_message(message.chat.id, "Ошибка! Вы ввели не число! Повторите ввод!")
