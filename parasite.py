import keeper
import collector
import scheduler
import submitter
import time
from datetime import datetime, timedelta
import atexit
import logging


from logging.handlers import TimedRotatingFileHandler

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
class Parasite():
    main_loop_period = 30
    mode = "default"
    collection_time = ("23","30")

    reddit_username = 'Euphetar'
    reddit_password = 'euphemia'
    reddit_app_client_id = 'nx4V0XjGKQzn1w'
    reddit_app_secret = 'M14znK5n2NaEwE5WkfqE4t7M_6Q'
    imgur_client_id = "528278d1320c1f3"
    imgur_secret = "e4eb6b131bec9f11aa934823fadcb695a7bbe73e"

    vk_app_id = "5380535"
    vk_secret_key = "ACMuuAwx0p4jj2yGmtzH"
    vk_group_id = "118173804"
    vk_user_login = "kururugisuzakueuphe@ya.ru"
    vk_user_password = "угзруьшф"

    target_subreddit = "Funnypics"
    target_category = "hot"
    target_amount = 1
    pics_path = 'pics/'

    schedule = [
        ("8:30", "old"),

        ("9:00", "new"),

        ("10:30", "new"),

        ("12:15", "new"),

        ("13:30", "new"),

        ("14:45", "old"),

        ("16:00", "new"),

        ("17:00", "old"),

        ("18:00", "new"),

        ("19:00", "new"),

        ("21:35", "new"),

        ("22:05", "old"),

        ("23:00", "old"),
    ]

    # total old: 5
    # total new: 8

    def __init__(self):
        self.target_subreddit = "Funnypics"
        self.target_category = "hot"
        self.target_amount = 20
        self.pics_path = 'pics/'
        self.prefix = "funny"

        self.keeper = keeper.Keeper(self.prefix)

        self.collector = collector.Collector(self.reddit_username, self.reddit_password, self.reddit_app_client_id, self.reddit_app_secret,self.imgur_client_id,self.imgur_secret, self.target_subreddit,self.target_category,self.target_amount,self.pics_path,  keeper = self.keeper)

        self.submitter = submitter.Submitter(self.vk_group_id, self.vk_app_id, self.vk_secret_key, self.vk_user_login, self.vk_user_password)

        self.scheduler = scheduler.Scheduler(self.keeper, self.schedule)
        self._upcoming = None

    @property
    def upcoming(self):
        return self._upcoming

    @upcoming.setter
    def upcoming(self, value):
        if value:
            logger.debug("Upcoming set to %s", str(value[1]))
        else:
            logger.debug("Upcoming set to None")
        self._upcoming = value

    def post_upcoming(self):
        img = self.keeper.get_image(self.upcoming[2])
        self.submitter.post_image(img)
        self.keeper.remove_from_schedule(self.upcoming)

    def tick(self):
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)
        collection_datetime = today + timedelta(hours=int(self.collection_time[0]), minutes=int(self.collection_time[1]))

        if now >= collection_datetime and abs(collection_datetime - now) <= timedelta(minutes=5):
            logger.debug("Collection_datetime %s", str(collection_datetime))
            self.keeper.dump_schedule()
            logger.debug("Dumped schedule")
            logger.debug("Collecting")
            self.collector.collect()
            if self.mode != 'collect_only':
                logger.debug("Constructing schedule")
                self.scheduler.construct_schedule()
                self.upcoming = self.keeper.get_upcoming_post()
                logger.debug("Upcoming post %s", str(self.upcoming))

        if self.mode != 'collect_only':
            if not self.upcoming:
                self.upcoming = self.keeper.get_upcoming_post()
                if not self.upcoming:
                    logger.debug('Out of posts, waiting for collection.')

            if now >= self.upcoming[1] and abs(self.upcoming[1] - now) <= timedelta(minutes=5):
                logger.debug("Posting time %s", str(self.upcoming[1]))
                logger.debug("Posting upcoming")
                self.post_upcoming()
                self.upcoming = self.keeper.get_upcoming_post()

    def clean_up(self):
        logger.debug("Cleaning up")
        self.keeper.clean_up()

    def main_loop(self):
        try:
            logger.debug("Started main loop")
            do_every(self.main_loop_period, self.tick)
        except Exception as e:
            logger.debug("Main loop shut down with exception %s", str(e) )
        finally:
            self.clean_up()



log_path = './logs/log'
logger = logging.getLogger('parasite_logger')
logger.setLevel(logging.DEBUG)

fh = TimedRotatingFileHandler(log_path, when="d", interval = 1, backupCount = 10)
fh.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s|%(message)s')
console.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(console)
logger.addHandler(fh)

parasite = Parasite()
atexit.register(parasite.clean_up)
parasite.main_loop()

