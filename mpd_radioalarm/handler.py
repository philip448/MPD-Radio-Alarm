from tornado.web import RequestHandler
from tornado.gen import coroutine
from peewee import DoesNotExist

from mpd_radioalarm.error import *
from mpd_radioalarm.data.model import *
from mpd_radioalarm.data import in_thread, password
from mpd_radioalarm import config

class BaseHandler(RequestHandler):
    def initialize(self):
        self.error_messages = []

    @coroutine
    def prepare(self):

        @in_thread
        def get_user():
            return self.get_current_user()

        user = yield get_user()

        if not user:
            self.redirect('/login')

    def get_current_user(self):
        session_token = self.get_secure_cookie('session')
        if not session_token:
            self.current_user = None
            return False

        try:
            # decode bytes, secure cookie received as bytes
            self.session = Session.get(token=session_token.decode())
            self.current_user = self.session.user
            return self.current_user

        except DoesNotExist:
            self.error_messages.append(ERR_INVALID_SESSION_TOKEN())
            return None

class WebHandler(BaseHandler):
    def get(self):
        self.write("It works!")

class LoginHandler(BaseHandler):
    def prepare(self):
        pass

    @coroutine
    def get(self):
        req = self.get_argument('req', default='/')

        @in_thread
        def get_user():
            return self.get_current_user()
        user = yield get_user()
        if user:
            return self.redirect(req)

        self.render('login.html', req=req)

    @coroutine
    def post(self):
        email = self.get_argument('email')
        pw = self.get_argument('password')
        req = self.get_argument('req')

        @in_thread
        def get_user():
            try:
                u = User.get(email=email)
                return u
            except DoesNotExist:
                return None

        user = yield get_user()
        if not user:
            self.error_messages.append(ERR_USER_NOT_FOUND())
            return self.render('login.html', req=req)

        if user.password != password(pw):
            self.error_messages.append(ERR_INVALID_PASSWORD())
            return self.render('login.html', req=req)

        @in_thread
        def create_session():
            t = Session.create(user=user)
            t.save()
            return t
        session = yield create_session()
        self.set_secure_cookie('session', session.token)
        return self.redirect(req)

