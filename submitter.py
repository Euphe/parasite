#!/usr/bin/python
# -*- coding: utf-8 -*-

import vk
import requests
import logging
import json
logger = logging.getLogger('parasite_logger')

class Submitter():
    def __init__(self, group_id, app_id, secret_key,user_login, user_password, polls_question, keeper=None):
        self.app_id = app_id
        self.secret_key = secret_key
        self.group_id = group_id
        self.user_login = user_login
        self.user_password = user_password
        self.polls_question = polls_question
        
        self.keeper = keeper
        #self.session = vk.Session(self.get_access_token())
        #self.api = vk.API(self.app_id, self.user_login, self.user_password)
        logger.debug("Initializing session")
        self.session = vk.AuthSession(app_id=self.app_id, user_login=self.user_login, user_password=self.user_password, scope="offline,photos,groups,wall")
        self.api = vk.API(self.session)
        logger.debug("Submitter initialized")

    def post(self, entry):
        try:
            entry_type = entry[3]
            if entry_type == "poll":
                return self.post_poll(entry[2])
            else:
                img = self.keeper.get_image(entry[2][0])
                return self.post_image(img)
        except Exception as e:
            logger.debug("Failed to post with exceiption: %s", str(e))

    def post_poll(self, images):

        def create_poll_id(poll):
            return 'poll'+str(self.group_id)+'_'+str(poll["poll_id"])

        logger.debug("Posting poll")
        poll = self.api.polls.create(question=self.polls_question,owner_id='-'+self.group_id, add_answers=json.dumps([str(x+1) for x in range(len(images))]) )

        uploaded = []
        for i in range(len(images)):
            image = self.keeper.get_image(images[i])
            uploaded.append(self.upload_image(image))
        #logger.debug(str(poll))
        attachments = ",".join([ str(save_data["id"]) for save_data in uploaded ])+','+str(create_poll_id(poll))
        logger.debug("Attachments: %s", attachments)
        self.api.wall.post(owner_id = "-"+self.group_id, from_group=True, attachments=attachments)

        for img in images:
            self.keeper.set_posted([img])
        logger.debug("Posted poll")

    def upload_image(self, img):
        logger.debug("Uploading image")
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

        return save_data

    def post_image(self, img):
        logger.debug("Posting image")
        save_data = self.upload_image(img)
        attachments = str(save_data["id"])
        self.api.wall.post(owner_id = "-"+self.group_id, from_group=True, attachments=attachments)
        self.keeper.set_posted([img])
        logger.debug("Posted image")

    def test(self):
        print(self.api.users.get(user_ids=1))