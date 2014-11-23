#!/usr/bin/env python
# coding: utf-8

from lib.query import Query

class SocialauthModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "ge_user_socialauth"
        super(SocialauthModel, self).__init__()

    def get_sa_by_suid_and_provider(self, suid, provider):
        where = "so_uid=%s and provider='%s'" % (suid, provider)
        return self.where(where).find()

    def add_new_socialauth(self, info):
        return self.data(info).add()

