#!/usr/bin/python
# -*- coding: utf-8 -*-


import praw
import os
import urllib
import re
import datetime

import imgurpython
try:
    from urllib.request import urlretrieve  # Python 3
except ImportError:
    from urllib import urlretrieve  # Python 2

from bs4 import BeautifulSoup

uri_name_ptrn = re.compile(r'\w+\.jpg|png/?$')

import logging
logger = logging.getLogger('parasite_logger')
import pytz

import socket
socket.setdefaulttimeout(30)

from util import utc_time_to_russian
class Collector():
    def __init__(self, username, password, app_client_id, app_secret,imgur_client_id,imgur_secret,targets,pics_path, timezone, keeper = None):
        self.username = username
        self.password = password
        self.app_client_id = app_client_id
        self.app_secret = app_secret
        self.imgur_client_id = imgur_client_id
        self.imgur_secret = imgur_secret
        self.timezone = timezone
        self.targets = targets
        self.pics_path = pics_path

        self.r = praw.Reddit(user_agent='collector_learn')

        self.imgur_client = imgurpython.ImgurClient(self.imgur_client_id, self.imgur_secret)

        self.keeper = keeper



    def make_soup(self, url):
        html = urllib.request.urlopen(url).read()
        return BeautifulSoup(html, "html.parser")

    def get_imgur_image(self, url):
        img= self.imgur_client.get_image(url.split('/')[-1])
        return img.link

    def download_photo(self, img_url, filename):
        return urlretrieve(img_url, filename)

    def filter_by_post_rules(self, posts, post_rules):
        return [ post for post in posts if post.score > post_rules["minimal score"] and post.over_18 == (post_rules["over 18"] if post_rules["over 18"] != "Any" else post.over_18) ]

    def get_subr_posts(self, sub, category, limit, post_rules, retry=0):
        if retry >= 3:
            raise(Exception("Too many retries getting sub %s, couldn't collect sub."%(str(sub))))

        try:
            if category == "hot":
                posts = self.filter_by_post_rules(list(sub.get_hot(limit=limit)), post_rules)
            elif category == "new":
                posts = self.filter_by_post_rules(list(sub.get_new(limit=limit)), post_rules)
            else:
                raise(Exception("Unknown reddit category"))

            return posts
        except praw.errors.HTTPException as e:
            logger.debug("Caught HTTP exception when retrieving sub %s cat %s", str(sub), str(category))
            logger.debug(e)
            logger.debug("Retry number: %d", retry)
            return self.get_subr_posts(sub, category, limit, post_rules, retry+1)

    def collect(self):
        posts = []
        for target in self.targets:
            logger.debug("Collecting target: %s",str(target))
            rsub = target["subreddit"]
            post_rules = target["post_rules"]
            category = target["category"]
            target_amount = target["target_amount"]

            sub = self.r.get_subreddit(rsub)

            #filter out bad posts
            target_posts = self.get_subr_posts(sub, category, target_amount*3, post_rules)
            posts = posts + target_posts

            target_posts = sorted(target_posts, key=lambda post:post.score, reverse=True)

            target_posts, successes, failures = self.store(target_posts, target_amount)

            self.remove_old_posts(successes)

    def get_url_and_name(self, uri):
        try:
            return uri, uri_name_ptrn.search(uri).group(0)
        except:
            #it's imgur or something
            if 'imgur' in uri:
                #its imgur, scrap it!
                imgur_uri = self.get_imgur_image(uri)
                return imgur_uri, uri_name_ptrn.search(imgur_uri).group(0)
            else:
                raise(Exception('Unknown website:' + uri))

    def store(self, posts, target_amount):
        logger.debug('Collector:storing posts')
        #abs_path = os.path.abspath(__file__)
        failures = 0
        successes = 0
        for post in posts:
            try:
                post.url, name = self.get_url_and_name(post.url)
                path = self.pics_path + name
                if self.keeper:
                    self.keeper.add_image([(None, utc_time_to_russian(datetime.datetime.utcnow()), post.url, path)])
                image = self.download_photo(post.url, path)
                logger.debug("Collected %s", post.url)
                successes+=1
                if successes >= target_amount:
                    break
            except Exception as e:
                logger.exception(e)
                logger.debug('Failed to download pic')
                failures+=1
        logger.debug('Storing complete:\n%d sucessful\n%d failed', successes, failures)
        return posts, successes, failures

    def remove_old_posts(self, amount):
        paths = self.keeper.delete_old_posts(amount)
        logger.debug("Removing files from system")
        for path in paths:
            os.remove(path)
        logger.debug("Removed files from system")