from loader import bot
from loguru import logger
from telebot.types import CallbackQuery
from states.user_states import User_input_state
from handlers.input_data import my_calendar


@bot.callback_query_handler(func=lambda call: call.data.isalpha())
def need_photo_callback(call: CallbackQuery) -> None:
    """
        Пользователь нажал кнопку "ДА" или "НЕТ"
        : param call: "yes" or "no"
        : return : None
        """

    if call.data == 'yes':
        logger.info('Нажата кнопка "ДА"')

        with bot.retrieve_data(call.message.chat.id) as data:
            data['photo_need'] = call.data

        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.set_state(call.message.chat.id, User_input_state.photo_count)
        bot.send_message(call.message.chat.id, '<b>Сколько вывести фотографий? <u>От 1 до 10!</u></b>', parse_mode="html")

    elif call.data == 'no':
        logger.info('Нажата кнопка "НЕТ"')

        with bot.retrieve_data(call.message.chat.id) as data:
            data['photo_need'] = call.data
            data['photo_count'] = '0'

        bot.delete_message(call.message.chat.id, call.message.message_id)
        my_calendar(call.message, 'заезда')