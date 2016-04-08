#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import getopt 
import keeper
import collector
import scheduler
import submitter
import time
from datetime import datetime, timedelta, MINYEAR
import atexit
import logging
import traceback
import sys
import pytz
from logging.handlers import TimedRotatingFileHandler
from util import utc_time_to_russian
def do_every(period,f,*args):
    def g_tick():
        t = time.time()
        count = 0
        while True:
            count += 1
            yield max(t + count*period - time.time(),0)
    g = g_tick()
    while True:
        time.sleep(next(g))
        f(*args)


modes = ("collect_only", "default")
abs_path = os.path.dirname(os.path.realpath(sys.argv[0]))

logger = None

class Parasite():
    timezone = pytz.timezone('Europe/Moscow')
    main_loop_period = 30
    mode = "default"


    reddit_username = 'Euphetar'
    reddit_password = 'euphemia'
    reddit_app_client_id = 'nx4V0XjGKQzn1w'
    reddit_app_secret = 'M14znK5n2NaEwE5WkfqE4t7M_6Q'
    imgur_client_id = "528278d1320c1f3"
    imgur_secret = "e4eb6b131bec9f11aa934823fadcb695a7bbe73e"

    vk_app_id = "5380535"
    vk_secret_key = "ACMuuAwx0p4jj2yGmtzH"
    vk_user_login = "kururugisuzakueuphe@ya.ru"
    vk_user_password = "угзруьшф"

    

    # total old: 5
    # total new: 8

    def __init__(self):
        self.collection_time = ("01","00")
        self.schedule = [
            ("8:30", "old"),

            ("9:00", "new"),

            ("10:30", "new"),

            ("12:15", "new"),

            ("13:30", "new"),

            ("14:45", "old"),

            ("16:00", "new"),

            ("17:00", "old"),

            ("18:00", "new"),

            ("19:00", "poll"),

            ("21:35", "new"),

            ("22:05", "old"),

            ("23:00", "old"),
        ]
        
        self.targets = [
            {
                "subreddit": "Funnypics",
                "category": "hot",
                "post_rules": {
                    "minimal score": 1, #int
                    "over 18": False, #False, True, "Any"
                },
                "target_amount": 30
            },
            {
                "subreddit": "Daily_Funny_Pics",
                "category": "hot",
                "post_rules": {
                    "minimal score": 1, #int
                    "over 18": False, #False, True, "Any"
                },
                "target_amount": 30
            },
        ]
        self.polls_question = "Кто милее?"
        self.pics_path = abs_path+'/pics/'
        self.log_path = abs_path+'/logs/'
        self.prefix = "funny"

        self.vk_group_id = "118173804"

        self._upcoming = None
        self.waiting_for_collection = False
        self.last_collected = datetime(MINYEAR,1,1,1,1,1)
        self.last_posted = datetime(MINYEAR,1,1,1,1,1)
        self.force_collection = False 
        self.force_schedule_construction = False 




    @property
    def upcoming(self):
        return self._upcoming

    @upcoming.setter
    def upcoming(self, value):
        if value:
            value = list(value)
        logger.debug("Upcoming set to %s", str(value))
        self._upcoming = value

    def post_upcoming(self):
        logger.debug("Posting upcoming")
        self.submitter.post(self.upcoming)
        self.keeper.remove_from_schedule(self.upcoming)

    def tick(self):
        #logger.debug("Calculating dates")
        now = utc_time_to_russian(datetime.utcnow())
        today = datetime(now.year, now.month, now.day)
        collection_datetime = today + timedelta(hours=int(self.collection_time[0]), minutes=int(self.collection_time[1]))
        #print(self.force_collection)
        #logger.debug("Calculated dates")
        if self.force_collection or (now >= collection_datetime and abs(collection_datetime - now) <= timedelta(minutes=5) and abs(self.last_collected - now) >= timedelta(minutes=5) ):

            if self.force_collection:
                self.force_collection = False
                logger.debug("Forced collection at %s", str(now))
            else:
                logger.debug("Collection_datetime %s", str(collection_datetime))
            self.keeper.dump_schedule()
            logger.debug("Dumped schedule")
            logger.debug("Collecting")
            self.collector.collect()
            self.last_collected = utc_time_to_russian(datetime.utcnow())
            self.waiting_for_collection = False
            if self.mode != 'collect_only':
                logger.debug("Constructing schedule")
                self.scheduler.construct_schedule()

            logger.debug("Finished collection")

        if self.force_schedule_construction:
            logger.debug("Forced constructing schedule")
            self.scheduler.construct_schedule()
        if not self.waiting_for_collection:
            if self.mode != 'collect_only':
                if not self.upcoming:
                    logger.debug('Getting new upcoming post')
                    try:
                        self.upcoming = self.keeper.get_upcoming_post()
                        logger.debug("Upcoming post %s", str(self.upcoming))
                    except Exception as e:
                        logger.debug("Caught exception")
                        logger.exception(e)
                        self.waiting_for_collection = True
                        logger.debug('Out of posts, waiting for collection.')

                if self.upcoming and now >= self.upcoming[1] and abs(self.upcoming[1]  - now) <= timedelta(minutes=5) and abs(self.last_posted - now) >= timedelta(minutes=5):
                    logger.debug("Posting time %s", str(self.upcoming[1]))
                    logger.debug('Last posted %s', str(self.last_posted))
                    self.post_upcoming()
                    self.last_posted = utc_time_to_russian(datetime.utcnow())
                    self.upcoming = None

    def clean_up(self):
        logger.debug("Cleaning up")
        self.keeper.clean_up()

    def main_loop(self):
        try:
            logger.debug("Started main loop")
            do_every(self.main_loop_period, self.tick)
        except Exception as e:
            logger.debug("Main loop shut down with exception")
            logger.exception(e)

    def start(self,argv):
        try:  
            opts, args = getopt.getopt(argv, "fc", ["force_collection","force_schedule_construction"])
        except getopt.GetoptError:
            print('invalid params')
            sys.exit(2)   

        for opt, arg in opts:     
            #print(opt)                                      
            if opt in ('-f', "--force_collection"):
                #print('Force collection enabled')
                self.force_collection = True
            elif opt in ('-c', "--force_schedule_construction"):
                self.force_schedule_construction = True

        atexit.register(self.clean_up)
        global logger
        logger = logging.getLogger('parasite_logger')
        logger.setLevel(logging.DEBUG)



        if not os.path.exists( os.path.dirname(self.log_path) ):
            os.makedirs( self.log_path)

        fh = TimedRotatingFileHandler(self.log_path+"/log", when="d", interval = 1, backupCount = 10)
        fh.setLevel(logging.DEBUG)
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s|%(message)s')
        console.setFormatter(formatter)
        fh.setFormatter(formatter)
        logger.addHandler(console)
        logger.addHandler(fh)

        if not os.path.exists(self.pics_path):
            os.makedirs(self.pics_path)

        logger.debug(self.log_path)
        logger.debug(self.pics_path)
        
        self.keeper = keeper.Keeper(self.timezone, self.prefix)
        self.collector = collector.Collector(self.reddit_username, self.reddit_password, self.reddit_app_client_id, self.reddit_app_secret,self.imgur_client_id,self.imgur_secret, self.targets ,self.pics_path, self.timezone, keeper = self.keeper)
        self.submitter = submitter.Submitter(self.vk_group_id, self.vk_app_id, self.vk_secret_key, self.vk_user_login, self.vk_user_password, self.polls_question, keeper = self.keeper)
        self.scheduler = scheduler.Scheduler(self.keeper, self.timezone, self.schedule)

        
        self.main_loop()



if __name__ == "__main__":
    parasite = Parasite()
    parasite.start(sys.argv[1:])


