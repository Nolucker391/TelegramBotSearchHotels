import api
import processing_json
import random
import database

from loader import bot
from telebot.types import Message, Dict, InputMediaPhoto
from loguru import logger


def find_and_show_hotels(message: Message, data: Dict) -> None:
    """
    Формирование запросов на поиск отелей, и детальной информации о них (адрес, фотографии).
    Вывод полученных данных пользователю в чат.
    : param message : Message
    : param data : Dict данные, собранные от пользователя
    : return : None
    """

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": data["destination_id"]},
        "checkInDate": {
            "day": int(data["checkInDate"]["day"]),
            "month": int(data["checkInDate"]["month"]),
            "year": int(data["checkInDate"]["year"]),
        },
        "checkOutDate": {
            "day": int(data["checkOutDate"]["day"]),
            "month": int(data["checkOutDate"]["month"]),
            "year": int(data["checkOutDate"]["year"]),
        },
        "rooms": [{"adults": 2, "children": [{"age": 5}, {"age": 7}]}],
        "resultsStartingIndex": 0,
        "resultsSize": 30,
        "sort": data["sort"],
        "filters": {
            "price": {"max": int(data["price_max"]), "min": int(data["price_min"])}
        },
    }

    url = "https://hotels4.p.rapidapi.com/properties/v2/list"

    response_hotels = api.general_request.request("POST", url, payload)
    logger.info(f"Сервер вернул ответ {response_hotels.status_code}")

    count = 0

    if response_hotels.status_code == 200:

        hotels = processing_json.get_hotels.get_hotels(
            response_hotels.text,
            data["command"],
            data["price_min"],
            data["price_max"],
            data["landmark_in"],
            data["landmark_out"],
        )
        if "error" in hotels:
            bot.send_message(message.chat.id, hotels["error"])
            bot.send_message(
                message.chat.id,
                "<b>Что-то пошло не так...</b>\n"
                "Попробуйте осуществить поиск с другими параметрами",
                parse_mode="html",
            )
            bot.send_message(message.chat.id, "")

        elif hotels == {}:
            bot.send_message(
                message.chat.id,
                "<b>Увы... Ничего не нашлось :(</b> \nПопробуйте осуществить поиск с другими параметрами",
                parse_mode="html",
            )

        for hotel in hotels.values():

            if count < int(data["quantity_hotels"]):
                count += 1
                summary_payload = {
                    "currency": "USD",
                    "eapid": 1,
                    "locale": "en_US",
                    "siteId": 300000001,
                    "propertyId": hotel["id"],
                }
                summary_url = "https://hotels4.p.rapidapi.com/properties/v2/get-summary"
                get_summary = api.general_request.request(
                    "POST", summary_url, summary_payload
                )
                logger.info(f"Сервер вернул ответ {get_summary.status_code}")

                if get_summary.status_code == 200:

                    summary_info = processing_json.get_summary.hotel_info(
                        get_summary.text
                    )

                    caption = (
                        f'<b>Название отеля:</b> {hotel["name"]}.\n'
                        f'<b>Адрес</b>: {summary_info["address"]}.\n'
                        f'<b>Стоимость проживания в сутки:</b> {round(hotel["price"], 2)}   $\n'
                        f'<b>Общая стоимость за {int(data["checkOutDate"]["day"]) - int(data["checkInDate"]["day"])} ночей:</b> {hotel["total_price"]}\n'
                        f'<b>Расстояние до центра:</b> {round(hotel["distance"], 2)} mile.\n'
                        f"<b>Внимание!</b> <u>Цены указаны с учетом налогов и сборов.</u>\n"
                    )

                    medias = []
                    links_to_images = []

                    try:
                        for random_url in range(int(data["photo_count"])):
                            links_to_images.append(
                                summary_info["images"][
                                    random.randint(0, len(summary_info["images"]) - 1)
                                ]
                            )
                    except (KeyError, ValueError):
                        continue

                    data_to_db = {
                        hotel["id"]: {
                            "name": hotel["name"],
                            "address": summary_info["address"],
                            "total": hotel["total_price"],
                            "price": hotel["price"],
                            "distance": round(hotel["distance"], 2),
                            "date_time": data["date_time"],
                            "images": links_to_images,
                        }
                    }

                    database.add_user_in_database.add_response(data_to_db)

                    if int(data["photo_count"]) > 0:

                        for number, url in enumerate(links_to_images):
                            if number == 0:
                                medias.append(
                                    InputMediaPhoto(
                                        media=url, caption=caption, parse_mode="html"
                                    )
                                )
                            else:
                                medias.append(InputMediaPhoto(media=url))

                        logger.info("Выдаю найденную информацию в чат")

                        bot.send_media_group(message.chat.id, medias)

                    else:
                        logger.info("Выдаю найденную информацию в чат")

                        bot.send_message(message.chat.id, caption, parse_mode="html")

                else:
                    bot.send_message(
                        message.chat.id,
                        f"<b>Что-то пошло не так, код ошибки: {get_summary.status_code}</b>\n"
                        f"Попробуйте осуществить поиск с другими параметрами",
                        parse_mode="html",
                    )
            else:
                break
        else:
            bot.send_message(
                message.chat.id,
                f"По заданным критериям нашел только - <b><u>{count} отелей.</u></b>",
                parse_mode="html",
            )
    else:
        bot.send_message(
            message.chat.id,
            f"<b>Что-то пошло не так, код ошибки: {response_hotels.status_code}</b>\n"
            f"Попробуйте осуществить поиск с другими параметрами",
            parse_mode="html",
        )

    bot.send_message(message.chat.id, f"<b>Поиск окончен!</b>\n", parse_mode="html")
