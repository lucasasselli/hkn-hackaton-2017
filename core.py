import logging,urllib,json,eventbot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup

pending_dict = dict() #dizionario utente_id -> funzioni

tags = ["#iot","#tecnolo","asda","asdasd","qwtwt","as3qtwg","otktop","asijdoapkd","ookokè","aposdoakso","aiopqowieqpo",
        "sadanidknaskd","#asdwq","okokpqo","opkkpo"] #list per debug

# starting setup
def keyboard(bot, update):

    # keyboard = [[InlineKeyboardButton("13-18", callback_data='1'),
    #                            InlineKeyboardButton("18-26", callback_data='2')],
    #
    #                            [InlineKeyboardButton("26-35", callback_data='3'),
    #                             InlineKeyboardButton("35-35+", callback_data='4')]]
    # reply_markup = InlineKeyboardMarkup(keyboard)
    #
    # update.message.reply_text("Inserisci la tua fascia di età:" , reply_markup=reply_markup)

    reply_keyboard = [['15-18', '18-26'],
                      ['26-35', '35-35+']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        "Seleziona la tua età: ",
        reply_markup=markup)

def start(bot, update):
    logging.debug("Invio al server %s",update.message.text)
    update.message.reply_text("Inserisci la città: ")
    pending_dict[update.message.chat.id] = posizione

def posizione(bot,update):
    logging.debug("Invio al server %s", update.message.text)
    pending_dict[update.message.chat.id] = raggio
    reply_keyboard = [['10km', '50km'],
                      ['100km', 'Verso l\'infinito e oltre']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        "Seleziona il raggio massimo d'interesse: ",
        reply_markup=markup)

def raggio(bot,update):
    logging.debug("Invio al server %s", update.message.text)
    del pending_dict[update.message.chat.id]
# fine setup


def uid_parser(uid):
    # TODO Implement core
    return 0

# add tag
def tag_graph(bot,update):
    reply_keyboard = create_listsoflists()
    markup = ReplyKeyboardMarkup([["Done"]]+reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        "Selezione i tags a cui sei interessato: ",
        reply_markup=markup)
    pending_dict[update.message.chat.id] = add_tag;

def create_listsoflists():
    print(eventbot.list_tags())
    return list(group(tags,3))


def group(lst, n):
    for i in range(0, len(lst), n):
        val = lst[i:i + n]
        if len(val) == n:
            yield tuple(val)

def add_tag(bot, update):
    logging.debug("Invio al server %s", update.message.text)

#fine add tag

# gestione input
def cmd_parser(bot,update):
    msg_text = update.message.text
    cmd = msg_text[1:]
    uid = update.message.chat.id

    if cmd == "start":
        # Start command

        update.message.reply_text("Benvenuto!")
        keyboard(bot,update)
        pending_dict[uid] = start
    elif cmd == "add":
        pending_dict[uid] = add_tag
        tag_graph(bot,update)
    else:
        update.message.reply_text("Comando non riconosciuto!")

    return 0


def msg_parser(bot, update):
    msg_text = update.message.text
    uid = update.message.chat.id

    logging.debug("New message from %s: %s", uid, msg_text)

    uid_parser(uid)

    if msg_text:
        if uid in pending_dict:
            # Pending argument
            logging.debug("Argument inserted!")
            arg_parser(bot, update)


def arg_parser(bot, update):
    uid = update.message.chat.id
    logging.debug("Parsing argument for dictionary")
    pending_dict[uid](bot, update)

#fine gestione input
