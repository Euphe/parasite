#!/usr/bin/python
# -*- coding: utf-8 -*-


from datetime import datetime, timedelta
import random
import pytz 

def utc_to_local(utc_dt, tz):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(tz)
    return tz.normalize(local_dt) 

def local_time(utc_dt, tz):
    return utc_to_local(utc_dt, tz)


class Scheduler():
	def __init__(self, keeper, timezone, schedule = []):
		self.schedule_blueprint = schedule
		self.keeper = keeper
		self.timezone = timezone

	def construct_schedule(self):
		schedule = []
		now = local_time(datetime.utcnow(), self.timezone)
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

			if pools[post_type]:
				img = random.choice(pools[post_type])
				if img:
					schedule.append( (post_time, img[0], post_type) )
					posted.append( img )
					pools[post_type].remove( img )
		self.keeper.set_posted(posted)
		self.schedule = schedule
		self.store_schedule(schedule)

	def store_schedule(self, schedule):
		self.keeper.store_schedule(schedule)