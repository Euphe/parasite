#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import random
import datetime
import pytz
import logging
from util import utc_time_to_russian
logger = logging.getLogger('parasite_logger')
class Keeper():
    def __init__(self, timezone, prefix = "default"):
        self.prefix = prefix
        self.connection = sqlite3.connect(self.prefix+'_pics.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
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
        logger.debug('Getting img')
        return self.cursor.execute('select * from '+self.prefix+'_images WHERE id = '+str(img_id)).fetchone()

    def get_last_image(self):
        return self.cursor.execute('select * from '+self.prefix+'_images').fetchone()

    def dump_schedule(self):
        logger.debug('Dumping schedule')
        schedule = self.cursor.execute('select * from '+self.prefix+'_schedule WHERE post_type = \'new\';').fetchmany()
        for post in schedule:
            img_id = post[2]
            self.cursor.execute('UPDATE '+self.prefix+'_images SET posted = 0 WHERE  id = '+str(img_id)+';')

        self.cursor.execute('''DELETE FROM '''+self.prefix+'''_schedule;''')
        self.cursor.execute('''VACUUM;''')

        self.connection.commit()

    def delete_old_posts(self, amount):
        logger.debug('Deleting %d old posts', amount)

        paths = self.cursor.execute('''SELECT path FROM '''+self.prefix+'''_images WHERE posted = 1 ORDER BY id DESC LIMIT '''+str(amount)+''';''').fetchall()
        self.cursor.execute('''DELETE FROM '''+self.prefix+'''_images WHERE id IN (SELECT id FROM '''+self.prefix+'''_images WHERE posted = 1 ORDER BY id DESC LIMIT '''+str(amount)+''');''')
        self.connection.commit()
        logger.debug("Deleted old posts from db")
        #print(str(paths))
        return [path[0] for path in paths]

    def store_schedule(self, schedule):
        logger.debug('Storing schedule')
        values = schedule
        self.cursor.executemany("INSERT INTO "+self.prefix+"_schedule VALUES (Null, ?, ?, ?)", values)
        self.connection.commit()

    def remove_from_schedule(self, post):
        logger.debug('Deleting from schedule')
        post_id = post[0]
        self.cursor.execute('''DELETE FROM '''+self.prefix+'''_schedule WHERE id = '''+str(post_id))
        self.connection.commit()

    def get_upcoming_post(self):
        sql = 'select * from '+self.prefix+'_schedule WHERE datetime(date) > datetime(\''+utc_time_to_russian(datetime.datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S")+'\') ORDER BY datetime(date)  ASC LIMIT 1 ;'
        logger.debug('SQL: %s', sql)

        post = self.cursor.execute(sql).fetchone()
        if not post:
            raise(Exception("No upcoming post"))
        logger.debug('Fetched upcoming post: %s', str(post) )
        return post

    def get_pool(self, post_type):
        logger.debug('Getting pools')
        if post_type == "new":
            return self.cursor.execute('select * from '+self.prefix+'_images where posted = 0').fetchall()
        else:
            return self.cursor.execute('select * from '+self.prefix+'_images where posted = 1').fetchall()

    def set_posted(self, imgs):
        logger.debug('Setting posted')
        for img in imgs:
            img_id = img[0]
            self.cursor.execute('UPDATE '+self.prefix+'_images SET posted = 1 WHERE  id = '+str(img[0])+';')
        self.connection.commit()

    def clean_up(self):
        self.connection.close()