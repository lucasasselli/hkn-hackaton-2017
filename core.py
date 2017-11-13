import logging
import connection
from connection import User
import utils
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import telegram


pending_dict = dict()  # dizionario utente_id -> funzioni
user_dict = dict()  # dizionario utente_id -> nuovo oggetto utente

global tag_list
tag_list = None

# starting setup


def inline_event(bot, update):
    query = update.callback_query
    uid = query.from_user.id
    eventid = query.data[1:]
    action = query.data[0]

    event = connection.get_event_by_eventid(eventid)

    if action == "0":
        logging.info("Utente %s partecipa a evento %s", uid, eventid)
        if connection.subscribe_user(str(uid), eventid, 0):
            bot.answer_callback_query(callback_query_id=query.id, text="Iscritto!")
        else:
            bot.answer_callback_query(callback_query_id=query.id, text="Sei già iscritto!")
    elif action == "2":
        logging.info("Utente %s abbandona evento %s", uid, eventid)
        if connection.unsubscribe_user(str(uid), eventid):
            bot.answer_callback_query(callback_query_id=query.id, text="Non partecipi più a questo evento!")
        else:
            bot.answer_callback_query(callback_query_id=query.id, text="Non sei iscritto a questo evento!")
    elif action == "3":
        bot.send_message(chat_id=uid, text="Non ancora implementato. Per prova @shopbot")
    elif action == "4":
        bot.send_location(chat_id=uid, latitude=event.lat, longitude=event.lon, text=event.place)
    else:
        logging.info("Utente %s chiede info per evento %s", uid, eventid)
        bot.send_message(chat_id=uid,
                         text='<b>' + event.name + '</b>\n\nInizio: ' + event.start.strftime("%H:%M:%S %d-%m-%Y") + '\nFine: ' + event.end.strftime("%H:%M:%S %d-%m-%Y") + '\nPosti rimanenti: ' + str(event.availability) + '\n\n<a href="' + event.url + '">Link</a>', parse_mode=telegram.ParseMode.HTML)


def start_step0(bot, update):
    """ Step 0 del login, inserisce età """
    user = User()
    user.uid = str(update.message.chat.id)

    reply_keyboard = [['15-18', '18-26'],
                      ['26-35', '35+']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        "Seleziona la tua età: ",
        reply_markup=markup)

    pending_dict[update.message.chat.id] = start_step1
    user_dict[update.message.chat.id] = user


def start_step1(bot, update):
    """ Step 1 del login, inserisci città """

    markup = telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton('Invia posizione', request_location=True)]],
                                          one_time_keyboard=True)
    update.message.reply_text(text="Dove ti trovi: ", reply_markup=markup)

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
                      ['100km', '500km']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        "Seleziona il raggio massimo d'interesse: ",
        reply_markup=markup)
    pending_dict[update.message.chat.id] = start_step3
    location = update.message.location
    user_dict[update.message.chat.id].lat = location.latitude
    user_dict[update.message.chat.id].lon = location.longitude


def start_step3(bot, update):
    user_dict[update.message.chat.id].radius = int(update.message.text[:-2])

    # Crea utente
    connection.create_user(user_dict[update.message.chat.id])

    # Togli da macchina a stati
    del pending_dict[update.message.chat.id]
    del user_dict[update.message.chat.id]

    update.message.reply_text("Utente registrato correttamente! Digita /list per l'elenco dei comandi")

# fine setup


# add tag
def tag_graph(bot, update):
    reply_keyboard = create_listsoflists()
    markup = ReplyKeyboardMarkup([["Fine"]] + reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        "Selezione i tags a cui sei interessato: ",
        reply_markup=markup)
    pending_dict[update.message.chat.id] = add_tag


def create_listsoflists():
    global tag_list
    tag_list = connection.list_tags()

    name_list = list()
    for tag in tag_list:
        name_list.append(tag.name)

    tag_grouped = utils.group(name_list, 3)

    return tag_grouped


def add_tag(bot, update):
    if(update.message.text == "Fine"):
        markup = telegram.ReplyKeyboardRemove(True)
        update.message.reply_text(
            "Tutti i tag inseriti",
            reply_markup=markup)
        pending_dict[update.message.chat.id] = end_tag
        return
    global tag_list
    if not tag_list:
        logging.debug("Taglist locale nulla!")
        tag_list = connection.list_tags()
    for tag in tag_list:
        if tag.name == update.message.text:
            logging.debug("inserisco %s", tag.name)
            tagid = tag.tagid
            success = connection.add_tag(str(update.message.chat.id), tagid)
            if success:
                update.message.reply_text("Tag aggiunto")
            else:
                update.message.reply_text("Tag già presente")
            return


def end_tag(bot, update):
    if(update.message.text == "Si"):
        tag_graph(bot, update)
    else:
        del pending_dict[update.message.chat.id]
# fine add tag

# gestione input


def cmd_parser(bot, update):
    msg_text = update.message.text
    cmd = msg_text[1:]
    uid = update.message.chat.id

    logging.debug("Nuovo comando da %s: %s", uid, msg_text)

    valid = connection.user_exists(str(update.message.chat.id))

    if cmd == "start":
        # Start command
        if not valid:
            update.message.reply_text("Benvenuto!")
            start_step0(bot, update)
        else:
            update.message.reply_text("Sei già loggato... Digita /logout per uscire.")
        return

    # Se non è start controlla il login
    if not valid:
        update.message.reply_text("Non sei connesso al sistema!\n Invia /start per cominciare.")
        return

    if cmd == "add":
        # Add tag
        pending_dict[uid] = add_tag
        tag_graph(bot, update)
    elif cmd == "suggest":
        # Suggested
        event_list = connection.list_events(False)
        user_tags = connection.get_tags_of_user(str(uid))
        if len(user_tags) > 0:
            for event in event_list:
                print(event.tags)
                for tag in user_tags:
                    if tag in event.tags:
                        print_event_button(bot, uid, event)
                        break

        else:
            update.message.reply_text("Non hai tag impostati! Usa /add per aggiungerli.")
    elif cmd == "myevents":
        event_list = connection.get_event_by_uid(str(uid))
        if len(event_list) > 0:
            for event in event_list:
                print_event_button(bot, uid, event, False)
        else:
            update.message.reply_text("Non partecipi a nessun evento!")
    elif cmd == "mytags":
        tags = connection.get_user_by_uid(str(uid)).tags
        if len(tags) > 0:
            for tag in tags:
                update.message.reply_text(tag.name)
        else:
            update.message.reply_text("Nessun tag attivo!")
    elif cmd == "list":
        update.message.reply_text("/add - Aggiungi un nuovo tag\n/suggest - Mostra gli eventi suggeriti\n/myevents - I miei eventi\n/mytags - I miei tag\n/logout - Logout dal sistema")
    elif cmd == "logout":
        connection.user_delete(str(uid))
        update.message.reply_text("Ci dispiace vederti andare via! :(")
    else:
        update.message.reply_text("Comando non riconosciuto!")


def msg_parser(bot, update):
    msg_text = update.message.text
    uid = update.message.chat.id
    position = update.message.location
    logging.debug("Nuovo messaggio da %s: %s", uid, msg_text)

    if msg_text or position:
        if uid in pending_dict:
            # Pending argument
            logging.debug("Argument inserted!")
            arg_parser(bot, update)
        else:
            update.message.reply_text("Input non valido!")


def arg_parser(bot, update):
    uid = update.message.chat.id
    logging.debug("Parsing argument for pending command")
    pending_dict[uid](bot, update)


def print_event_button(bot, uid, event, join=True):
    if not join:
        if event.price > 0:
            keyboard = [[InlineKeyboardButton("Paga ora", callback_data=str(3) + event.eventid),
                         InlineKeyboardButton("Abbandona", callback_data=str(2) + event.eventid)],
                        [InlineKeyboardButton("Info", callback_data=str(1) + event.eventid),
                         InlineKeyboardButton("Posizione", callback_data=str(4) + event.eventid)]]
        else:
            keyboard = [[InlineKeyboardButton("Abbandona", callback_data=str(2) + event.eventid)],
                        [InlineKeyboardButton("Info", callback_data=str(1) + event.eventid),
                         InlineKeyboardButton("Posizione", callback_data=str(4) + event.eventid)]]
    else:
        keyboard = [[InlineKeyboardButton("Partecipa", callback_data=str(0) + event.eventid)],
                    [InlineKeyboardButton("Info", callback_data=str(1) + event.eventid),
                     InlineKeyboardButton("Posizione", callback_data=str(4) + event.eventid)]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if event.price == 0:
        price = "Gratis"
    else:
        price = str(event.price) + " €"

    text = event.name + " - " + price
    bot.send_photo(chat_id=uid, photo=event.imageurl, reply_markup=reply_markup, caption=text)

# fine gestione input
