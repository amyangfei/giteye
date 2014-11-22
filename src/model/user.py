#!/usr/bin/env python
# coding: utf-8

from lib.query import Query

class UserModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "ge_user"
        super(UserModel, self).__init__()

    def get_user_by_uid(self, uid):
        where = "uid = %s" % uid
        return self.where(where).find()

    def get_user_by_email(self, email):
        where = "email = '%s'" % email
        return self.where(where).find()

    def get_user_by_username(self, username):
        where = "username = '%s'" % username
        return self.where(where).find()

    def set_user_base_info_by_uid(self, uid, info):
        where = "uid = %s" % uid
        return self.data(info).where(where).save()

    def set_user_avatar_by_uid(self, uid, avatar_name):
        where = "uid = %s" % uid
        return self.data({
            "avatar": avatar_name
        }).where(where).save()

    def set_user_password_by_uid(self, uid, secure_password):
        where = "uid = %s" % uid
        return self.data({
            "password": secure_password
        }).where(where).save()

    def add_new_user(self, info):
        return self.data(info).add()

    def get_all_users_count(self):
        return self.count()

