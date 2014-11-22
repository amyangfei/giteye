#!/usr/bin/env python
# coding: utf-8

from base import BaseHandler

class IndexHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["user_info"]["counter"] = {
                #"topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                #"replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                #"favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }

            #template_variables["notifications_count"] = self.notification_model.get_user_unread_notification_count(user_info["uid"]);

        template_variables["status_counter"] = {
            "users": self.user_model.get_all_users_count(),
        }
        #template_variables["topics"] = self.topic_model.get_all_topics(current_page = page)
        self.render("topic/index.html", **template_variables)

