import handler.topic
import handler.user

handlers = [
    (r"/", handler.topic.IndexHandler),
    (r"/register", handler.user.RegisterHandler),
    (r"/login", handler.user.LoginHandler),
    (r"/logout", handler.user.LogoutHandler),
    (r"/oauth/(?P<provider>[a-z]+)", handler.user.OauthHandler),
    (r"/oauth/callback/(?P<provider>[a-z]+)", handler.user.OauthCallbackHandler),
]
