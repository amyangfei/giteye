#!/usr/bin/env python
# coding: utf-8

import time
import tornado.web

import config
from lib.soapi import soproxy
from base import BaseHandler
from form.user import RegisterForm, LoginForm
from lib.utils import rand_salt, password_hash, random_name
from lib.social import GithubAPIClient

def do_login(self, uid):
    user_info = self.user_model.get_user_by_uid(uid)
    uid = user_info["uid"]
    self.session["uid"] = uid
    self.session["username"] = user_info["username"]
    self.session["email"] = user_info["email"]
    self.session.save()
    self.set_secure_cookie("user", str(uid))

def do_logout(self):
    # destroy sessions
    self.session["uid"] = None
    self.session["username"] = None
    self.session["email"] = None
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

        uid = self.user_model.add_new_user(user_info)
        if(uid):
            do_login(self, uid)

        self.redirect("/")


def _get_client(provider):
    if provider == 'github':
        return GithubAPIClient(config.client_id_github,
                config.client_secret_github,
                redirect_uri=config.redirect_uri_github)
    return None


def _register_by_oauth(self, access_token, so_user, provider):
    username = soproxy.make_api_call(provider, 'get_user_soname', so_user)
    if username is None:
        username = random_name()

    user_info = {
        "email": "",
        "password": "",
        "username": username,
        "created": time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    uid = self.user_model.add_new_user(user_info)

    if(uid):
        social_uid = soproxy.make_api_call(provider, 'get_user_soid', so_user)
        so_uname = soproxy.make_api_call(provider, 'get_user_soname', so_user)
        social_info = {
            "uid": uid,
            "provider": provider,
            "so_uid": social_uid,
            "so_username": so_uname if so_uname else "",
            "access_token": access_token,
        }
        so_ret = self.socialauth_model.add_new_socialauth(social_info)
        print so_ret

        do_login(self, uid)


class OauthHandler(BaseHandler):
    def get(self, provider, template_variables = {}):
        client = _get_client(provider)
        if client is None:
            template_variables["errors"] = \
                    {"invalid_provicer": [u"错误的第三方"]}
            self.render("user/login.html", **template_variables)
        else:
            auth_url = client.get_authorize_url()
            self.redirect(auth_url)


class OauthCallbackHandler(BaseHandler):
    def get(self, provider, template_variables = {}):
        oauth_code = self.get_argument('code')
        self.session['%s_oauth_code' % provider] = oauth_code
        client = _get_client(provider)
        resp = client.request_access_token(oauth_code)
        if 'access_token' not in resp:
            template_variables["errors"] = \
                    {"request access_token failed": [u"获取access_token失败"]}
            self.render("user/login.html", **template_variables)
        else:
            so_user = soproxy.make_api_call(
                    provider, 'get_user_info', resp['access_token'])
            so_uid = soproxy.make_api_call(
                    provider, 'get_user_soid', so_user)
            socialauth = self.socialauth_model.\
                    get_sa_by_suid_and_provider(so_uid, provider)
            if socialauth:
                do_login(self, socialauth.uid)
            else:
                _register_by_oauth(self, resp['access_token'], so_user, provider)

            self.redirect('/')

