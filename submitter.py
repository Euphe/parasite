#!/usr/bin/python
# -*- coding: utf-8 -*-

import vk
import requests
import logging
logger = logging.getLogger('parasite_logger')

class Submitter():
    def __init__(self, group_id, app_id, secret_key,user_login, user_password, keeper=None):
        self.app_id = app_id
        self.secret_key = secret_key
        self.group_id = group_id
        self.user_login = user_login
        self.user_password = user_password
        
        self.keeper = keeper
        #self.session = vk.Session(self.get_access_token())
        #self.api = vk.API(self.app_id, self.user_login, self.user_password)
        logger.debug("Initializing session")
        self.session = vk.AuthSession(app_id=self.app_id, user_login=self.user_login, user_password=self.user_password, scope="offline,photos,groups,wall")
        self.api = vk.API(self.session)
        logger.debug("Submitter initialized")


    def post_image(self, img):
        logger.debug("Posting image")
        upload_server = self.api.photos.getWallUploadServer(group_id=self.group_id)
        upload_url = upload_server["upload_url"]
        path = img[3]
        link = img[2]
        name= path.split("/")[-1]
        try:
            with open(path, 'rb') as f:
                r = requests.post(upload_url, files={"photo": f})
        except IOError as e:
            logger.exception(e)
            logger.debug("Picture file not found, img: %s", img)
            return None
            
        json = r.json()
        save_data = self.api.photos.saveWallPhoto(group_id=self.group_id,photo=json["photo"],server=json["server"],hash=json["hash"] )[0]
        
        attachments = str(save_data["id"])
        self.api.wall.post(owner_id = "-"+self.group_id, from_group=True, attachments=attachments)
        logger.debug("Posted image")

    def test(self):
        print(self.api.users.get(user_ids=1))