from telebot.types import BotCommand
from config_data.config import DEFAULT_COMMANDS

def set_default_commands(bot):

    bot.set_my_commands(
        [BotCommand(*index) for index in DEFAULT_COMMANDS]
    )