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
                core.print_event_button(bot, user.uid, event)
