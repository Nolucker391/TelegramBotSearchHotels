from telebot.handler_backends import State, StatesGroup


class User_input_state(StatesGroup):
    """
    Класс для запоминания состояния пользователя

    """

    command = State()
    input_city = State()
    id_destination = State()
    quantity_hotels = State()
    photo_count = State()
    input_date = State()
    minimum_price = State()
    maximum_price = State()
    land_mark_in = State()
    land_mark_out = State()
    history_select = State()
