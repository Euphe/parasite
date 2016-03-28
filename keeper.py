#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import random
import datetime
import pytz
def utc_to_local(utc_dt, tz):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(tz)
    return tz.normalize(local_dt) 

def local_time(utc_dt, tz):
    return utc_to_local(utc_dt, tz)

class Blob:
    """Automatically encode a binary string."""
    def __init__(self, s):
        self.s = s

    def _quote(self):
        return "'%s'" % sqlite3.Binary(self.s)

class Keeper():
    def __init__(self, timezone, prefix = "default"):
        self.prefix = prefix
        self.connection = sqlite3.connect('parasite.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.cursor = self.connection.cursor()
        self.init_schema()
        self.timezone = timezone

    def init_schema(self):    
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS '''+self.prefix+'''_images(id INTEGER  PRIMARY KEY, date timestamp, link text UNIQUE, path text UNIQUE, posted INTEGER)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS '''+self.prefix+'''_schedule(id INTEGER  PRIMARY KEY, date timestamp, image_id INTEGER, post_type text)''')

        self.connection.commit()

    def add_image(self, values):
        # Insert a row of data
        self.cursor.executemany("INSERT INTO "+self.prefix+"_images VALUES (?, ?, ?, ?, 0)", values)
        self.connection.commit()

    def get_image(self, img_id):
        return self.cursor.execute('select * from '+self.prefix+'_images WHERE id = '+str(img_id)).fetchone()

    def get_last_image(self):
        return self.cursor.execute('select * from '+self.prefix+'_images').fetchone()

    def dump_schedule(self):
        schedule = self.cursor.execute('select * from '+self.prefix+'_schedule WHERE post_type = \'new\';').fetchmany()
        for post in schedule:
            img_id = post[2]
            self.cursor.execute('UPDATE '+self.prefix+'_images SET posted = 0 WHERE  id = '+str(img_id)+';')

        self.cursor.execute('''DELETE FROM '''+self.prefix+'''_schedule;''')
        self.cursor.execute('''VACUUM;''')

        self.connection.commit()


    def store_schedule(self, schedule):
        values = schedule
        self.cursor.executemany("INSERT INTO "+self.prefix+"_schedule VALUES (Null, ?, ?, ?)", values)
        self.connection.commit()

    def remove_from_schedule(self, post):
        post_id = post[0]
        self.cursor.execute('''DELETE FROM '''+self.prefix+'''_schedule WHERE id = '''+str(post_id))
        self.connection.commit()

    def get_upcoming_post(self):
        return self.cursor.execute('select * from '+self.prefix+'_schedule WHERE datetime(date) > datetime(\''+local_time(datetime.datetime.utcnow(), self.timezone).strftime("%Y-%m-%d %H:%M:%S")+'\') ORDER BY datetime(date)  ASC LIMIT 1 ;').fetchone()

    def get_pool(self, post_type):
        if post_type == "new":
            return self.cursor.execute('select * from '+self.prefix+'_images where posted = 0').fetchall()
        else:
            return self.cursor.execute('select * from '+self.prefix+'_images where posted = 1').fetchall()

    def set_posted(self, imgs):
        for img in imgs:
            img_id = img[0]
            self.cursor.execute('UPDATE '+self.prefix+'_images SET posted = 1 WHERE  id = '+str(img[0])+';')
        self.connection.commit()

    def get_img_for_type(self, post_type):
        post = None
        if post_type == "new":
            posts = self.cursor.execute('select * from '+self.prefix+'_images where posted = 0').fetchall()
        elif post_type == "old":
            posts = self.cursor.execute('select * from '+self.prefix+'_images where posted = 1').fetchall()

        if posts:
            post = random.choice(posts)
            self.cursor.execute('UPDATE '+self.prefix+'_images SET posted = 1 WHERE  id = '+str(post[0])+';')
            self.connection.commit()
        return post

    def clean_up(self):
        self.connection.close()