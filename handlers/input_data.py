from loader import bot
from telebot.types import Message
from loguru import logger
import datetime
from states.user_states import User_input_state
import keyboards.inline
import api
from keyboards.calendar.telebot_calendar import Calendar
import processing_json
from utils.print_data import print_data
import database


@bot.message_handler(commands=["lowprice", "highprice", "bestdeal"])
def low_high_best_handler(message: Message) -> None:
    """
    Обработчик команд, срабатывает на три команды /lowprice, /highprice, /bestdeal
    и запоминает необходимые данные. Спрашивает пользователя - какой искать город.
    : param message : Message
    : return : None
    """
    bot.set_state(message.chat.id, User_input_state.command)

    with bot.retrieve_data(message.chat.id) as data:
        data.clear()
        logger.info("Запоминаем выбранную команду: " + message.text)
        data["command"] = message.text
        data["sort"] = check_command(message.text)
        data["date_time"] = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        data["chat_id"] = message.chat.id

    database.add_user_in_database.add_user(
        message.chat.id, message.from_user.username, message.from_user.full_name
    )
    bot.set_state(message.chat.id, User_input_state.input_city)

    bot.send_message(
        message.from_user.id,
        f"Вы выбрали команду <u>{message.text}.</u> "
        f"Давайте уточним детали запроса...\n"
        f"<b>Введите город, в котором нужно найти отель (на латинице):</b> ",
        parse_mode="html",
    )


@bot.message_handler(state=User_input_state.input_city)
def input_city(message: Message) -> None:
    """
    Ввод пользователем города и отправка запроса серверу на поиск вариантов городов.
    Возможные варианты городов передаются генератору клавиатуры.
    : param message : Message
    : return : None
    """
    with bot.retrieve_data(message.chat.id) as data:
        data["input_city"] = message.text
        logger.info("Пользователь ввел город: " + message.text)
        # Создаем запрос для поиска вариантов городов и генерируем клавиатуру

        url = "https://hotels4.p.rapidapi.com/locations/v3/search"
        querystring = {"q": message.text, "locale": "en_US"}
        response_cities = api.general_request.request("GET", url, querystring)

        if response_cities.status_code == 200:
            possible_cities = processing_json.get_cities.get_city(response_cities.text)
            keyboards.inline.city_buttons.show_cities_buttons(message, possible_cities)
        else:
            bot.send_message(
                message.chat.id,
                f"<b>Что-то пошло не так, <u>код ошибки: {response_cities.status_code}</u></b>\n"
                f"Нажмите команду еще раз. И введите другой город.",
                parse_mode="html",
            )

            data.clear()


@bot.message_handler(state=User_input_state.quantity_hotels)
def input_quantity(message: Message) -> None:
    """
    Ввод количества выдаваемых на странице отелей, а так же проверка, является ли
    введённое числом и входит ли оно в заданный диапазон от 1 до 25
    : param message : Message
    : return : None
    """
    try:
        if message.text.isdigit():
            if 0 < int(message.text) <= 10:
                logger.info("Ввод и запись количества отелей: " + message.text)

                with bot.retrieve_data(message.chat.id) as data:
                    data["quantity_hotels"] = message.text

                bot.set_state(message.chat.id, User_input_state.minimum_price)
                bot.send_message(
                    message.chat.id,
                    "Супер! Теперь уточним стоимость отеля за ночь(сутки)."
                    "<b>\nВведите <u>минимальную стоимость</u> отеля в долларах $ США:</b>",
                    parse_mode="html",
                )
            else:
                bot.send_message(
                    message.chat.id,
                    "Неправильный ввод! <b><u>Вводимое число должен быть в диапазоне от 1 до 10!</u></b> Повторите ввод.",
                    parse_mode="html",
                )

        elif int(message.text) < 0:
            bot.send_message(
                message.chat.id,
                "Неправильный ввод! <b><u>Вводимое число не может быть меньше 0!</u></b> Повторите ввод.",
                parse_mode="html",
            )
        else:
            raise ValueError

    except ValueError:
        bot.send_message(
            message.chat.id,
            "Неправильный ввод! <b><u>Вы ввели не число!</u></b> Повторите ввод.",
            parse_mode="html",
        )


@bot.message_handler(state=User_input_state.minimum_price)
def input_price_min(message: Message) -> None:
    """
    Ввод минимальной стоимости отеля и проверка чтобы это было число.
    : param message : Message
    : return : None
    """

    try:
        if message.text.isdigit():
            logger.info("Ввод и запись минимальной стоимости отеля: " + message.text)

            with bot.retrieve_data(message.chat.id) as data:
                data["price_min"] = message.text
            bot.set_state(message.chat.id, User_input_state.maximum_price)
            bot.send_message(
                message.chat.id,
                "Записал..."
                "\n<b>Теперь введите <u>максимальную стоимость</u> отеля в долларах $ США:</b>",
                parse_mode="html",
            )

        elif int(message.text) < 0:
            bot.send_message(
                message.chat.id,
                "Неправильный ввод! <b><u>Вводимое число не может быть меньше 0!</u></b> Повторите ввод.",
                parse_mode="html",
            )
        else:
            raise ValueError

    except ValueError:
        bot.send_message(
            message.chat.id,
            "Неправильный ввод! <b><u>Вы ввели не число!</u></b> Повторите ввод.",
            parse_mode="html",
        )


@bot.message_handler(state=User_input_state.maximum_price)
def input_price_max(message: Message) -> None:
    """
    Ввод максимальной стоимости отеля и проверка чтобы это было число. Максимальное число не может
    быть меньше минимального.
    : param message : Message
    : return : None
    """

    try:
        if message.text.isdigit():
            logger.info(
                "Ввод и запись максимальной стоимости отеля, сравнение с price_min: "
                + message.text
            )

            with bot.retrieve_data(message.chat.id) as data:
                if int(data["price_min"]) < int(message.text):
                    data["price_max"] = message.text
                    keyboards.inline.photo_need.show_buttons_photo_need_yes_no(message)
                else:
                    bot.send_message(
                        message.chat.id,
                        "Неправильный ввод! <b><u>Максимальная цена должна быть больше минимальной!</u></b> Повторите ввод.",
                        parse_mode="html",
                    )

        elif int(message.text) < 0:
            bot.send_message(
                message.chat.id,
                "Неправильный ввод! <b><u>Вводимое число не может быть меньше 0!</u></b> Повторите ввод.",
                parse_mode="html",
            )

        else:
            raise ValueError

    except ValueError:
        bot.send_message(
            message.chat.id,
            "Неправильный ввод! <b><u>Вы ввели не число!</u></b> Повторите ввод.",
            parse_mode="html",
        )


@bot.message_handler(state=User_input_state.photo_count)
def input_photo_quantity(message: Message) -> None:
    """
    Ввод количества фотографий и проверка на число и на соответствие заданному диапазону от 1 до 10
    : param message : Message
    : return : None
    """
    try:
        if message.text.isdigit():
            if 0 < int(message.text) <= 10:
                logger.info("Ввод и запись количества фотографий: " + message.text)
                with bot.retrieve_data(message.chat.id) as data:
                    data["photo_count"] = message.text
                my_calendar(message, "заезда")
            else:
                bot.send_message(
                    message.chat.id,
                    "Неправильный ввод! <b><u>Число фотографий должно быть в диапазоне от 1 до 10!</u></b> Повторите ввод",
                    parse_mode="html",
                )

        elif int(message.text) < 0:
            bot.send_message(
                message.chat.id,
                "Неправильный ввод! <b><u>Вводимое число не может быть меньше 0!</u></b> Повторите ввод.",
                parse_mode="html",
            )

        else:
            raise ValueError

    except ValueError:
        bot.send_message(
            message.chat.id,
            "Неправильный ввод! <b><u>Вы ввели не число!</u></b> Повторите ввод.",
            parse_mode="html",
        )


@bot.message_handler(state=User_input_state.land_mark_in)
def input_landmark_in(message: Message) -> None:
    """
    Ввод начала диапазона расстояния до центра
    : param message : Message
    : return : None
    """
    number = message.text.replace(",", ".")

    try:
        if message.text.isdigit() or float(number):
            with bot.retrieve_data(message.chat.id) as data:
                data["landmark_in"] = number

            bot.set_state(message.chat.id, User_input_state.land_mark_out)
            bot.send_message(
                message.chat.id,
                "<b>Введите <u>конец диапазона</u> расстояния от центра (<u>в милях</u>).</b>",
                parse_mode="html",
            )

        elif int(message.text) < 0:
            bot.send_message(
                message.chat.id,
                "Неправильный ввод! <b><u>Вводимое число не может быть меньше 0!</u></b> Повторите ввод.",
                parse_mode="html",
            )

        else:
            raise ValueError

    except ValueError:
        bot.send_message(
            message.chat.id,
            "Неправильный ввод! <b><u>Вы ввели не число!</u></b> Повторите ввод.",
            parse_mode="html",
        )


@bot.message_handler(state=User_input_state.land_mark_out)
def input_landmark_out(message: Message) -> None:
    """
    Ввод конца диапазона расстояния до центра
    : param message : Message
    : return : None
    """
    number = message.text.replace(",", ".")

    try:
        if message.text.isdigit() or float(number):
            with bot.retrieve_data(message.chat.id) as data:
                data["landmark_out"] = number
                print_data(message, data)
            bot.delete_state(message.from_user.id, message.chat.id)
        elif int(message.text) < 0:
            bot.send_message(
                message.chat.id,
                "Неправильный ввод! <b><u>Вводимое число не может быть меньше 0!</u></b> Повторите ввод.",
                parse_mode="html",
            )

        else:
            raise ValueError

    except ValueError:
        bot.send_message(
            message.chat.id,
            "Неправильный ввод! <b><u>Вы ввели не число!</u></b> Повторите ввод.",
            parse_mode="html",
        )


def check_command(command: str) -> str:
    """
    Проверка команды и назначение параметра сортировки
    : param command : str команда, выбранная (введенная) пользователем
    : return : str команда сортировки
    """
    if command == "/bestdeal":
        return "DISTANCE"
    elif command == "/lowprice" or command == "/highprice":
        return "PRICE_LOW_TO_HIGH"


bot_calendar = Calendar()


def my_calendar(message: Message, word: str) -> None:
    """
    Запуск инлайн-клавиатуры (календаря) для выбора дат заезда и выезда
    : param message : Message
    : param word : str слово (заезда или выезда)
    : return : None
    """
    bot.send_message(
        message.chat.id,
        f"Выберите дату: {word}",
        reply_markup=bot_calendar.create_calendar(),
    )
