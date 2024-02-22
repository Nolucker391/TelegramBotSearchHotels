import json
from telebot.types import Dict

def get_hotels(response_text: str, command: str, price_min: str, price_max: str, landmark_in: str, landmark_out: str) -> Dict:
    """
    Принимает ответ от сервера, выбранную команду сортировки, а так же пределы диапазона
    расстояния от центра города. Возвращает отсортированный словарь, в зависимости от команды сортировки.
    : param response_text : str Ответ от сервера, в котором содержится информация об отелях
    : param command : str Команда сортировки
    : param landmark_in : str Начало диапазона растояния до центра
    : param landmark_out : str Конец диапазона растояния до центра
    : return hotels_data : Dict Возвращает словарь с данными об отелях
    """

    data = json.loads(response_text)

    if not data:
        raise LookupError('Запрос пуст...')

    if 'errors' in data.keys():
        return {'error': data['errors'][0]['message']}

    hotels_data = {}

    for hotel in data['data']['propertySearch']['properties']:
        try:
            if float(price_min) < hotel['price']['lead']['amount'] < float(price_max):
                hotels_data[hotel['id']] = {
                    'name': hotel['name'], 'id': hotel['id'],
                    'distance': hotel['destinationInfo']['distanceFromDestination']['value'],
                    'unit': hotel['destinationInfo']['distanceFromDestination']['unit'],
                    'price': hotel['price']['lead']['amount'],
                    'total_price': hotel['price']['displayMessages'][1]['lineItems'][0]['value']
                }
        except (KeyError, TypeError):
            continue

    if command == '/highprice':
        hotels_data = {
            key: value for key, value in
            sorted(hotels_data.items(), key=lambda hotel_id: hotel_id[1]['price'], reverse=True)
        }

    elif command == '/bestdeal':
        hotels_data = {}

        for hotel in data['data']['propertySearch']["properties"]:
            try:
                if float(landmark_in) < hotel['destinationInfo']['distanceFromDestination']['value'] < float(landmark_out):
                    if float(price_min) < hotel['price']['lead']['amount'] < float(price_max):
                        hotels_data[hotel['id']] = {
                            'name': hotel['name'], 'id': hotel['id'],
                            'distance': hotel['destinationInfo']['distanceFromDestination']['value'],
                            'unit': hotel['destinationInfo']['distanceFromDestination']['unit'],
                            'price': hotel['price']['lead']['amount'],
                            'total_price': hotel['price']['displayMessages'][1]['lineItems'][0]['value']
                        }
            except (KeyError, TypeError):
                continue

    return hotels_data