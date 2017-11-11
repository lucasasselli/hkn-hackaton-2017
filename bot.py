from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import core
import logging
import secrets
import broadcast
from apscheduler.schedulers.background import BackgroundScheduler

# Costanti
CHECK_EVENT_PERIOD = 5

global updater
updater = Updater(secrets.BOT_TOKEN)


def poll_event():
    logging.info("Controllo notifica nuovi eventi...")
    broadcast.notify_new_events(updater.bot)


def main():
    # Logger
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Inizio...")
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)

    # Setup
    dp = updater.dispatcher

    # Parse input utente
    dp.add_handler(MessageHandler(Filters.text, core.msg_parser))
    dp.add_handler(MessageHandler(Filters.command, core.cmd_parser))

    scheduler = BackgroundScheduler()
    scheduler.add_job(broadcast.check_new_event, 'interval', seconds=5)
    scheduler.start()

    # Inizia il polling del bot
    updater.start_polling()
    updater.idle()

    # NON ATTRAVERSARE QUESTA LINEA
    #             |
    #             V
    # -----------------------------


if __name__ == '__main__':
    main()
