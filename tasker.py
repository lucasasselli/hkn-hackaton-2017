import sys
import logging
from apscheduler.schedulers.background import BackgroundScheduler

sys.path.insert(0, 'backend')


class Tasker:

    def __init__(self, period):
        self.sched = BackgroundScheduler()
        self.sched.add_job(self.__poll_event, 'interval', seconds=period)

    def start(self):
        self.sched.start()

    def __poll_event(self):
        logging.info("Controllo nuovi eventi per notifiche...")

    def broadcast_events(self):
        # TODO Check if a new event
        return 0
