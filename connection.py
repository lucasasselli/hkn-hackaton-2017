import googlemaps
import mysql.connector
import secrets
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


gmaps = googlemaps.Client(key='AIzaSyCnPNKvHYT6AWB77umnOkW_DQXfXKf3qU4')


def db_init():
    try:
        db = mysql.connector.connect(**secrets.config)
    except mysql.connector.Error as err:
        print(err)

    return db


def query(sql_query, table, idquery):
    db = db_init()
    cursor = db.cursor()
    query = "SELECT " + sql_query + " FROM " + table + " WHERE " + idquery
    logging.debug(query)
    cursor.execute(query)
    a = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return a


class Event:
    def from_sql(self, eventid):
        if eventid:
            self.eventid = str(eventid[0])
            self.name = query("name", "event", "eventid = " + str(eventid[0]))
            self.start = query("start", "event", "eventid = " + str(eventid[0]))
            self.end = query("end", "event", "eventid = " + str(eventid[0]))
            self.lat = query("lat", "event", "eventid = " + str(eventid[0]))
            self.lon = query("lon", "event", "eventid = " + str(eventid[0]))
            self.place = query("place", "event", "eventid = " + str(eventid[0]))
            self.description = query("description", "event", "eventid = " + str(eventid[0]))
            self.target = query("target", "event", "eventid = " + str(eventid[0]))
            self.price = query("price", "event", "eventid = " + str(eventid[0]))
            self.url = query("url", "event", "eventid = " + str(eventid[0]))
            self.imageurl = query("imageurl", "event", "eventid = " + str(eventid[0]))
            self.phone = query("phone", "event", "eventid = " + str(eventid[0]))
            self.availability = query("availability", "event", "eventid = " + str(eventid[0]))
            self.notified = query("notified", "event", "eventid = " + str(eventid[0]))
            self.tags = list()

            db = db_init()
            cursor = db.cursor()
            cursor.execute("SELECT tagid FROM event_tag WHERE eventid = " + str(eventid[0]) + ";")
            row = cursor.fetchone()
            while row is not None:
                tag = Tag()
                tag.from_sql(row)
                self.tags.append(tag)
                row = cursor.fetchone()
            cursor.close()
            db.close()


class User:
    def from_sql(self, uid):
        if uid:
            self.uid = str(uid[0])
            self.age = query("age", "user", "uid = " + str(uid[0]))
            self.lat = query("lat", "user", "uid = " + str(uid[0]))
            self.lon = query("lon", "user", "uid = " + str(uid[0]))
            self.radius = query("radius", "user", "uid = " + str(uid[0]))
            self.tags = []

            db = db_init()
            cursor = db.cursor()
            cursor.execute("SELECT tagid FROM user_tag WHERE uid = " + str(uid[0]) + ";")
            row = cursor.fetchone()
            while row is not None:
                tag = Tag()
                tag.from_sql(row)
                self.tags.append(tag)
                row = cursor.fetchone()
            cursor.close()
            db.close()


class Tag:
    def from_sql(self, tagid):
        self.tagid = str(tagid[0])
        self.name = query("name", "tag", "tagid = " + str(tagid[0]))


def flatlister(array):  # transforms list of tuples into flat list
    flat_list = []
    for sublist in array:
        for item in sublist:
            flat_list.append(item)
    return flat_list


def list_tags():  # get a list of all tags
    db = db_init()
    query = db.cursor()
    query.execute("SELECT tagid FROM tag;")
    row = query.fetchone()
    taglist = []
    while row is not None:
        tag = Tag()
        tag.from_sql(row)
        taglist.append(tag)
        row = query.fetchone()
    query.close()
    db.close()

    return taglist


def user_exists(uid):  # Get a boolean True if user exists
    exists = None
    db = db_init()
    query = db.cursor()
    query.execute("SELECT * FROM user WHERE uid='" + str(uid) + "'")
    query.fetchall()

    if(query.rowcount != 0):
        exists = True
    else:
        exists = False
    query.close()
    db.close()
    return exists


def create_user(user):  # Create a new user
    logger.info('Creating user')
    if not(user_exists(user.uid)):
        db = db_init()
        logger.info('Checking values')
        logger.debug('User: %s, Age: %i, Latitude: %f, Longitude: %f, Radius: %i',
                     user.uid, user.age, user.lat, user.lon, user.radius)
        query = db.cursor(buffered=False)
        query.execute("INSERT INTO user(uid, age, lat, lon, radius) VALUES ('" + user.uid + "'," +
                      str(user.age) + ", " + str(user.lat) + ", " + str(user.lon) + ", " + str(user.radius) + ");")
        db.commit()
        db.close()
        query.close()


def is_not_full(eventid):  # Returns True if event has available tickets
    db = db_init()
    query = db.cursor()
    query.execute("SELECT availability FROM event WHERE eventid='" + eventid + "';")
    a = (query.fetchone()[0] == 1)
    query.close()
    db.close()
    return a


def get_event_by_tag(taglist):  # Returns event(s) matching all queried tag IDs
    ##############
    # Parameter is NOT a python list!
    # Use get_event_by_tag('1, 2, 3')
    #############

    db = db_init()
    query = db.cursor()
    sql_query = 'SELECT event.eventid FROM event_tag, event WHERE event.eventid = event_tag.eventid AND event.availability > 0 AND event_tag.tagid IN (' + \
        taglist + ') GROUP BY event_tag.eventid;'
    query.execute(sql_query)
    row = query.fetchone()
    eventlist = []
    while row is not None:
        eventlist.append(Event(row))
        row = query.fetchone()
    query.close()
    db.close()
    return eventlist


def get_event_by_interval(start, end):  # Get all events within specified date-time range
    # Datetime format: "yyyy-mm-dd hh:mm:ss"
    db = db_init()
    query = db.cursor()
    query.execute("SELECT eventid FROM event WHERE start BETWEEN '" + start + "' AND '" + end + "';")
    row = query.fetchone()
    eventlist = []
    while row is not None:
        eventlist.append(Event(row))
        row = query.fetchone()
    query.close()
    db.close()
    return eventlist


def get_free_events():  # Get list of free events
    db = db_init()
    query = db.cursor()
    query.execute("SELECT eventid FROM event WHERE price = 0;")
    row = query.fetchone()
    eventlist = []
    while row is not None:
        eventlist.append(Event(row))
        row = query.fetchone()
    query.close()
    db.close()
    return eventlist


def is_event_notified(eventid):  # Returns True if event.notified = 1
    db = db_init()
    query = db.cursor()
    query.execute("SELECT notified FROM event WHERE eventid='" + eventid + "';")

    a = (query.fetchone()[0] == 1)
    query.close()
    db.close()
    return a


def list_events(unnotified_only):  # List all events with list_events(False)
    # Only not-notified events with list_events(True)
    db = db_init()
    query = db.cursor()

    if(unnotified_only):
        sql_query = "SELECT * FROM event WHERE notified = 0;"
    else:
        sql_query = "SELECT * FROM event;"

    query.execute(sql_query)
    data = query.fetchall()
    eventlist = list()

    for row in data:
        event = Event()
        event.eventid = str(row[0])
        event.name = row[1]
        event.start = row[2]
        event.end = row[3]
        event.lat = row[4]
        event.lon = row[5]
        event.place = row[6]
        event.description = row[7]
        event.target = row[8]
        event.price = row[9]
        event.url = row[10]
        event.imageurl = row[11]
        event.phone = row[12]
        event.availability = row[13]
        event.notified = row[14]
        event.tags = list()

        cursor = db.cursor()
        cursor.execute("SELECT tagid FROM event_tag u WHERE eventid = '" + event.eventid + "';")
        for (tagid) in cursor:
            event.tags.append(tagid[0])
        cursor.close()

        eventlist.append(event)

    query.close()
    db.close()

    return eventlist


def list_events_label():  # only events with free seats
    db = db_init()
    cursor = db.cursor()
    cursor.execute("SELECT eventid FROM event WHERE availability > 0;")
    row = cursor.fetchone()
    eventlist = []
    while row is not None:
        event = Event()
        event.from_sql(row)
        eventlist.append(event)
        row = cursor.fetchone()
    cursor.close()
    db.close()
    return eventlist


def get_all_users():  # list of all users
    db = db_init()
    query = db.cursor()
    query.execute("SELECT uid FROM user")
    row = query.fetchone()
    userlist = []
    while row is not None:
        user = User()
        user.from_sql(row)
        userlist.append(user)
        row = query.fetchone()
    query.close()
    db.close()
    return userlist


def get_event_by_uid(uid):  # List of the events joined by the user
    db = db_init()
    query = db.cursor()
    query.execute("SELECT eventid FROM event_user WHERE uid = '" + uid + "'")
    row = query.fetchone()
    eventlist = []
    while row is not None:
        event = Event()
        event.from_sql(row)
        eventlist.append(event)
        row = query.fetchone()
    query.close()
    db.close()
    return eventlist


def add_tag(uid, tagid):
    db = db_init()
    cursor = db.cursor()
    logging.debug('User: %s, Tag: %s', uid, tagid)
    cursor.execute("INSERT INTO user_tag(uid, tagid) VALUES ('" + uid + "', " + tagid + ");")
    db.commit()
    db.close()
    cursor.close()


def delete_tag(uid, tagid):
    db = db_init()
    cursor = db.cursor()
    cursor.execute("DELETE FROM user_tag WHERE uid='" + uid + "' AND tagid='" + tagid + "'")
    db.commit()
    db.close()
    cursor.close()


def set_notified(eventid):
    db = db_init()
    cursor = db.cursor()
    cursor.execute("UPDATE event SET notified=1 WHERE eventid='" + eventid + "'")
    db.commit()
    cursor.close()
    db.close()


def get_user_by_uid(uid):
    uidarray = []
    uidarray.append("'" + uid + "'")
    user = User()
    user.from_sql(uidarray)
    return user


def get_event_by_eventid(eventid):
    idarray = []
    idarray.append("'" + eventid + "'")
    event = Event()
    event.from_sql(idarray)
    return event


def subscribe_user(uid, eventid, payment):

    # Returns False if user is already subscribed
    # Otherwise subscribes and returns True. :)

    ret = None

    db = db_init()
    query = db.cursor()
    query.execute("SELECT COUNT(*) FROM event_user WHERE uid='" + uid + "' AND eventid='" + eventid + "'")
    ret = not (query.fetchone()[0] == 1)
    query.close()

    if(ret):
        cursor = db.cursor()
        cursor.execute("INSERT INTO event_user(uid, eventid, payment) VALUES ('" + uid + "', " + str(eventid) + ", " + str(payment) + ");")
        db.commit()
        cursor.execute("UPDATE event SET availability = availability -1 WHERE eventid='" + str(eventid) + "';")
        db.commit()
        cursor.close()

    db.close()

    return ret


def unsubscribe_user(uid, eventid):
    ret = None

    db = db_init()
    query = db.cursor()
    query.execute("SELECT COUNT(*) FROM event_user WHERE uid='" + uid + "' AND eventid='" + str(eventid) + "'")
    ret = (query.fetchone()[0] == 1)
    query.close()

    if ret:
        cursor = db.cursor()
        cursor.execute("DELETE FROM event_user WHERE uid='" + uid + "' AND eventid='" + str(eventid) + "'")
        db.commit()
        cursor.execute("UPDATE event SET availability = availability +1 WHERE eventid='" + str(eventid) + "';")
        db.commit()
        cursor.close()

    db.close()
    return ret


def user_delete(uid):
    db = db_init()
    cursor = db.cursor()
    cursor.execute("DELETE FROM event_user WHERE uid='" + uid + "'")
    db.commit()
    cursor.execute("DELETE FROM user_tag WHERE uid='" + uid + "'")
    db.commit()
    cursor.execute("DELETE FROM user WHERE uid='" + uid + "'")
    db.commit()
    cursor.close()
    db.close()


def get_tags_of_user(uid):
    db = db_init()
    cursor = db.cursor()
    cursor.execute("SELECT tagid FROM user_tag u WHERE uid = '" + uid + "';")
    x = []
    for (tagid) in cursor:
        x.append(tagid[0])

    cursor.close()
    db.close()
    return x
