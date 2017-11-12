import sys
sys.path.insert(0, 'backend')

import logging
import connection
import utils
import core
from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def notify_new_events(bot):
    user_list = connection.get_all_users()
    event_list = connection.list_events(True)

    for event in event_list:
        # Event
        for user in user_list:
            # User
            if utils.user_has_tags(user, event.tags):
                keyboard = [[InlineKeyboardButton("Parteciperò", callback_data=core.EventCallback(event.eventid, 0))],
                            [InlineKeyboardButton("Info", callback_data=core.EventCallback(event.eventid, 1))]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                # TODO Aggiunge messaggio
                bot.send_photo(chat_id=user.uid, photo=event.imageurl, reply_markup=reply_markup)
