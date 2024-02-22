from loader import bot
from telebot.types import CallbackQuery
from states.user_states import User_input_state

@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def destination_id_callback(call: CallbackQuery) -> None:

    if call.data:
        bot.set_state(call.message.chat.id, User_input_state.id_destination)

        with bot.retrieve_data(call.message.chat.id) as data:
            data['destination_id'] = call.data

        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.set_state(call.message.chat.id, User_input_state.quantity_hotels)

        bot.send_message(call.message.chat.id, 'Отлично! Записал...'
                                               '\n<b>Сколько вывести отелей в чат? <u>Не более 10!</u></b>', parse_mode="html")