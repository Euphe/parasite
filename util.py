from datetime import timedelta
def russian_time_to_utc(dtm):
	return dtm - timedelta(hours=3) #КОСТЫЛЬНАЯ МАГИЯ

def utc_time_to_russian(dtm):
	return dtm + timedelta(hours=3) #КОСТЫЛЬНАЯ МАГИЯ