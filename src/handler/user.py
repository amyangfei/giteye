#!/usr/bin/env python
# coding: utf-8

import time
import tornado.web

from base import BaseHandler
from form.user import RegisterForm, LoginForm
from lib.utils import rand_salt, password_hash

def do_login(self, user_id):
    user_info = self.user_model.get_user_by_uid(user_id)
    user_id = user_info["uid"]
    self.session["uid"] = user_id
    self.session["username"] = user_info["username"]
    self.session["email"] = user_info["email"]
    #self.session["password"] = user_info["password"]
    self.session.save()
    self.set_secure_cookie("user", str(user_id))

def do_logout(self):
    # destroy sessions
    self.session["uid"] = None
    self.session["username"] = None
    self.session["email"] = None
    #self.session["password"] = None
    self.session.save()

    # destroy cookies
    self.clear_cookie("user")

class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user_email = self.current_user['email']
        self.write(user_email)


class LoginHandler(BaseHandler):
    def get(self, template_variables = {}):
        do_logout(self)
        self.render("user/login.html", **template_variables)

    def post(self, template_variables = {}):
        template_variables = {}

        # validate the fields

        form = LoginForm(self)

        if not form.validate():
            self.get({"errors": form.errors})
            return

        # continue while validate succeed
        user_info = self.user_model.get_user_by_email(form.email.data)
        if user_info is None:
            template_variables["errors"] = {"invalid_email": [u"邮箱不存在"]}
            self.get(template_variables)

        secure_password = password_hash(form.password.data, user_info.salt)

        if(secure_password == user_info.password):
            do_login(self, user_info["uid"])
            # update `last_login`
            # self.user_model.set_user_base_info_by_uid(user_info["uid"], {"last_login": time.strftime('%Y-%m-%d %H:%M:%S')})
            self.redirect(self.get_argument("next", "/"))
            return
        else:
            template_variables["errors"] = {"invalid_password": [u"密码不正确"]}
            self.get(template_variables)

class LogoutHandler(BaseHandler):
    def get(self):
        do_logout(self)
        # redirect
        self.redirect(self.get_argument("next", "/"))

class RegisterHandler(BaseHandler):
    def get(self, template_variables = {}):
        do_logout(self)
        self.render("user/register.html", **template_variables)

    def post(self, template_variables = {}):
        template_variables = {}

        # validate the fields

        form = RegisterForm(self)

        if not form.validate():
            self.get({"errors": form.errors})
            return

        # validate duplicated

        duplicated_email = self.user_model.get_user_by_email(form.email.data)
        duplicated_username = self.user_model.get_user_by_username(form.username.data)

        if(duplicated_email or duplicated_username):
            template_variables["errors"] = {}

            if(duplicated_email):
                template_variables["errors"]["duplicated_email"] = [u"所填邮箱已经被注册过"]

            if(duplicated_username):
                template_variables["errors"]["duplicated_username"] = [u"所填用户名已经被注册过"]

            self.get(template_variables)
            return


        # continue while validate succeed

        salt = rand_salt(16)
        secure_password = password_hash(form.password.data, salt)

        user_info = {
            "email": form.email.data,
            "password": secure_password,
            "username": form.username.data,
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
            "salt": salt,
        }

        if(self.current_user):
            return

        user_id = self.user_model.add_new_user(user_info)

        if(user_id):
            do_login(self, user_id)

        self.redirect("/")
        #self.redirect(self.get_argument("next", "/"))

