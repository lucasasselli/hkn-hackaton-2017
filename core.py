import sys
sys.path.insert(0, 'backend')

import logging
import connection
from connection import User
import utils
import broadcast
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


class EventCallback():
    def __init__(self, eventid, callback):
        self.eventid = eventid
        self.callback = callback


pending_dict = dict()  # dizionario utente_id -> funzioni
user_dict = dict()  # dizionario utente_id -> nuovo oggetto utente

global tag_list
tag_list = None

# starting setup


def join_event(bot, update):
    query = update.callback_query
    uid = query.message.chat_id
    event_id = query.data
    logging.info("Utente %s partecipa a evento %s", uid, event_id)

    # bot.edit_message_text(text="Ci vediamo all'evento {}!".format(event_id),
    #                       chat_id=uid, message_id=query.message.message_id)


def start_step0(bot, update):
    """ Step 0 del login, inserisce età """
    user = User()
    user.uid = str(update.message.chat.id)

    reply_keyboard = [['15-18', '18-26'],
                      ['26-35', '35-35+']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        "Seleziona la tua età: ",
        reply_markup=markup)

    pending_dict[update.message.chat.id] = start_step1
    user_dict[update.message.chat.id] = user


def start_step1(bot, update):
    """ Step 1 del login, inserisci città """
    update.message.reply_text("Inserisci la città: ")

    pending_dict[update.message.chat.id] = start_step2
    text = update.message.text
    age = 0
    if text == "15-18":
        age = 1
    elif text == "18-26":
        age = 2
    elif text == "26-35":
        age = 3
    elif text == "35-35+":
        age = 4

    user_dict[update.message.chat.id].age = age


def start_step2(bot, update):
    """ Step 2 del login, inserisci raggio """
    reply_keyboard = [['10km', '50km'],
                      ['100km', 'Verso l\'infinito e oltre']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        "Seleziona il raggio massimo d'interesse: ",
        reply_markup=markup)
    pending_dict[update.message.chat.id] = start_step3
    user_dict[update.message.chat.id].lat = 0
    user_dict[update.message.chat.id].lon = 0


def start_step3(bot, update):
    user_dict[update.message.chat.id].radius = int(update.message.text[:-2])

    # Crea utente
    connection.create_user(user_dict[update.message.chat.id])

    # Togli da macchina a stati
    del pending_dict[update.message.chat.id]
    del user_dict[update.message.chat.id]

# fine setup


# add tag
def tag_graph(bot, update):

    reply_keyboard = create_listsoflists()
    markup = ReplyKeyboardMarkup([["Done"]] + reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        "Selezione i tags a cui sei interessato: ",
        reply_markup=markup)
    pending_dict[update.message.chat.id] = add_tag


def create_listsoflists():
    print(connection.list_tags())

    tag_list = connection.list_tags()
    name_list = list()

    for tag in tag_list:
        name_list.append(tag.name)

    tag_grouped = utils.group(name_list, 3)

    return tag_grouped


def add_tag(bot, update):
    if(update.message.text == "Done"):
        markup = ReplyKeyboardMarkup([["Si"], ["No"]], one_time_keyboard=True)
        update.message.reply_text(
            "I tags sono stati inseriti, vuoi continuare?",
            reply_markup=markup)
        pending_dict[update.message.chat.id] = end_tag
        return

    tagid = -1
    for tag in tag_list:
        if tag.name == update.message.text:
            tagid = tag.id

    if tagid >= 0:
        connection.add_tag(str(update.message.chat.id), tagid)
    else:
        update.message.reply_text("Tag non riconosciuto!")


def end_tag(bot, update):
    if(update.message.text == "Si"):
        tag_graph(bot, update)
    else:
        del pending_dict[update.message.chat.id]
# fine add tag

# gestione input


def check_user_valid(update):
    """ Controlla che l'utente esista """
    if not connection.user_exists(str(update.message.chat.id)):
        update.message.reply_text("Non sei connesso al sistema!\n Invia /start per cominciare.")
        return False
    else:
        return True


def cmd_parser(bot, update):
    msg_text = update.message.text
    cmd = msg_text[1:]
    uid = update.message.chat.id

    logging.debug("Nuovo comando da %s: %s", uid, msg_text)

    if cmd == "start":
        # Start command
        update.message.reply_text("Benvenuto!")
        start_step0(bot, update)
        return

    # Se non è start controlla il login
    if not check_user_valid(update):
        return

    if cmd == "add":
        # Add tag
        pending_dict[uid] = add_tag
        tag_graph(bot, update)
    elif cmd == "debug_event":
        # Debug event FIXME
        broadcast.__debug__send_event(bot, uid, 0)
        broadcast.__debug__send_event(bot, uid, 1)
    else:
        update.message.reply_text("Comando non riconosciuto!")


def msg_parser(bot, update):
    msg_text = update.message.text
    uid = update.message.chat.id

    logging.debug("Nuovo messaggio da %s: %s", uid, msg_text)

    # Controlla che l'utente sia loggato o stia effettuando login
    # if not check_user_valid(update) and uid not in user_dict:
    #     return

    if msg_text:
        if uid in pending_dict:
            # Pending argument
            logging.debug("Argument inserted!")
            arg_parser(bot, update)


def arg_parser(bot, update):
    uid = update.message.chat.id
    logging.debug("Parsing argument for pending command")
    pending_dict[uid](bot, update)

# fine gestione input
