#!/usr/bin/python
# -*- coding: utf-8 -*-


from datetime import datetime, timedelta
import random
import pytz 
from util import russian_time_to_utc


class Scheduler():
	def __init__(self, keeper, timezone, schedule = []):
		self.schedule_blueprint = schedule
		self.keeper = keeper
		self.timezone = timezone

	def construct_schedule(self):
		schedule = []
		now = russian_time_to_utc(datetime.utcnow())
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