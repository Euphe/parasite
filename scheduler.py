from datetime import datetime, timedelta
class Scheduler():
	def __init__(self, keeper, schedule = []):
		self.schedule_blueprint = schedule
		self.keeper = keeper

	def construct_schedule(self):
		schedule = []
		now = datetime.now()
		today = datetime(now.year, now.month, now.day)

		for entry in self.schedule_blueprint:
			time = entry[0].split(":")
			post_type = entry[1]
			post_time = today + timedelta(hours=int(time[0]), minutes=int(time[1]))

			post = self.keeper.get_img_for_type(post_type)
			if post:
				schedule.append( (post_time, post[0], post_type) )
		self.schedule = schedule
		self.store_schedule(schedule)

	def store_schedule(self, schedule):
		self.keeper.store_schedule(schedule)