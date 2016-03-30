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
    def __init__(self, username, password, app_client_id, app_secret,imgur_client_id,imgur_secret,target_subreddits,target_category,target_amount,pics_path, timezone, post_rules, keeper = None):
        self.username = username
        self.password = password
        self.app_client_id = app_client_id
        self.app_secret = app_secret
        self.imgur_client_id = imgur_client_id
        self.imgur_secret = imgur_secret
        self.timezone = timezone
        self.target_subreddits = target_subreddits
        self.target_category = target_category
        self.target_amount = target_amount
        self.pics_path = pics_path
        self.post_rules = post_rules


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

    def collect(self):
        posts = []
        for rsub in self.target_subreddits:
            sub = self.r.get_subreddit(rsub)
            if self.target_category == "hot":
                posts = posts + list(sub.get_hot(limit=self.target_amount*3))

        #filter out bad posts
        #we are only looking for posts with images or links, score over 0
        posts = [ post for post in posts if post.score > self.post_rules["minimal score"] and post.over_18 == (self.post_rules["over 18"] if self.post_rules["over 18"] != "Any" else post.over_18) ].sorted(key=lambda post:post.score, reverse=True)


        return self.store(posts)

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

    def store(self, posts):
        logger.debug('Collector:storing posts')
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
                if successes >= self.target_amount:
                    break
            except Exception as e:
                logger.exception(e)
                logger.debug('Failed to download pic')
                failures+=1
        logger.debug('Storing complete:\n%d sucessful\n%d failed', successes, failures)
        return posts