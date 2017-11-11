import sys
sys.path.insert(0, 'backend')

import logging
import connection
import utils


def notify_new_events(bot):
    user_list = None
    event_list = None

    for event in event_list:
        # Event
        tags = event.tags
        for user in user_list:
            # User
            if utils.user_has_tags(user, tags):
                bot.send_photo(chat_id=user.id, photo=open('tests/test.png', 'rb'))




