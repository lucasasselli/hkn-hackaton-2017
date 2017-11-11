from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import core
import logging
import secrets
from tasker import Tasker

CHECK_EVENT_PERIOD = 5


def main():

    # Logger
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Inizio...")
    logging.getLogger("telegram").setLevel(logging.WARNING)

    # Setup
    updater = Updater(secrets.BOT_TOKEN)
    dp = updater.dispatcher

    # Parse input utente
    dp.add_handler(MessageHandler(Filters.text, core.msg_parser))
    dp.add_handler(MessageHandler(Filters.command, core.cmd_parser))

    # Inizia il polling del bot
    updater.start_polling()
    updater.idle()

    tasker = Tasker(CHECK_EVENT_PERIOD)
    tasker.start()


if __name__ == '__main__':
    main()
