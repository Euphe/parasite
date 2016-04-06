#!/usr/bin/python
# -*- coding: utf-8 -*-


from datetime import datetime, timedelta
import random
import pytz 
from util import russian_time_to_utc, utc_time_to_russian
import logging
logger = logging.getLogger('parasite_logger')

class Scheduler():
    def __init__(self, keeper, timezone, schedule = []):
        self.schedule_blueprint = schedule
        self.keeper = keeper
        self.timezone = timezone

    def construct_schedule(self):
        schedule = []
        now = utc_time_to_russian(datetime.utcnow())
        today = datetime(now.year, now.month, now.day)
        pools = {
            'new':self.keeper.get_pool('new'),
            'old':self.keeper.get_pool('old')
        }
        posted = []
        for entry in tuple(self.schedule_blueprint):
            time = entry[0].split(":")
            post_type = entry[1]
            post_time = today + timedelta(hours=int(time[0]), minutes=int(time[1]))

            if post_type == "poll":
                pool = "new"
                img1 = random.choice(pools[pool])
                pools[pool].remove( img1 )
                posted.append( img1 )
                img2 = random.choice(pools[pool])
                pools[pool].remove( img2 )
                posted.append( img2 )

                schedule.append( (post_time, [img1[0],img2[0]], post_type) )
            else:
                try:
                    img = random.choice(pools[post_type])
                    if img:
                        schedule.append( (post_time, [img[0]], post_type) )
                        posted.append( img )
                        pools[post_type].remove( img )
                except Exception as e:
                    logger.exception(e)
                    logger.debug("Couldn't add schedule entry for blueprint %s", entry)

        self.schedule = schedule
        self.store_schedule(schedule)

    def store_schedule(self, schedule):
        self.keeper.store_schedule(schedule)