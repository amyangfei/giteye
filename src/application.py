#!/usr/bin/env python
# coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf8")

import os

import tornado.httpserver
import tornado.ioloop
import tornado.web
import torndb
from tornado.options import define, options
from jinja2 import Environment, FileSystemLoader
import redis

from lib.loader import Loader
from lib.session import SessionManager
from urls import handlers

define("port", default = 9999, help = "run on the given port", type=int)
define("mysql_host", default = "localhost", help = "community database host")
define("mysql_database", default = "giteye", help = "community database name")
define("mysql_user", default = "giteye", help = "community database user")
define("mysql_password", default = "mysql_db_password", help = "community database password")
define("redis_host", default = "localhost", help = "redis host")
define("redis_port", default = 6379, help = "redis port", type=int)
define("redis_db", default = 0, help = "redis db number", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            blog_title = u"Git Eye",
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies = True,
            cookie_secret = "cookie_secret_code",
            login_url = "/login",
            autoescape = None,
            jinja2 = Environment(loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")), trim_blocks = True),
            reserved = ["user", "topic", "home", "setting", "forgot", "login", "logout", "register", "admin"],
        )

        handlers.append(
            (r"/(favicon\.ico)", tornado.web.StaticFileHandler, dict(path = settings["static_path"])),
        )

        tornado.web.Application.__init__(self, handlers, **settings)

        # Have one global connection to the DB across all handlers
        self.db = torndb.Connection(
            host = options.mysql_host, database = options.mysql_database,
            user = options.mysql_user, password = options.mysql_password
        )

        # Have one global loader for loading models and handles
        self.loader = Loader(self.db)

        # Have one global model for db query
        self.user_model = self.loader.use("user.model")
        self.socialauth_model = self.loader.use("socialauth.model")

        # Have one global redis controller
        pool = redis.ConnectionPool(host=options.redis_host, port=options.redis_port, db=options.redis_db)
        self.rc = redis.StrictRedis(connection_pool=pool)

        # Have one global session controller
        self.session_manager = SessionManager(settings["cookie_secret"], self.rc, 86400 * 15)


def main():
    options.parse_config_file('./config.py')
    options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

