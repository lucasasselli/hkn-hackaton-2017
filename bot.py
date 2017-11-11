from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import core
import logging
import secrets


def main():

    # Logger
    logging.basicConfig(level=logging.DEBUG)

    # Setup
    updater = Updater(secrets.BOT_TOKEN)
    dp = updater.dispatcher

    # Parse stuff
    dp.add_handler(MessageHandler(Filters.text, core.msg_parser))
    dp.add_handler(MessageHandler(Filters.command, core.cmd_parser))

    # Start polling
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
