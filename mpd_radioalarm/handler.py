from tornado.gen import coroutine
from tornado.web import RequestHandler
from types import SimpleNamespace

from model import *
from mpd_radioalarm.concurrent import in_thread
from mpd_radioalarm import password
from mpd_radioalarm.error import *


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
        action = self.get_argument('action')

        if action == 'login':
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

        elif action == 'logout':
            session_token = self.get_secure_cookie('session')

            @in_thread
            def delete_session():
                # decode bytes, secure cookie received as bytes
                session = Session.get(token=session_token.decode())
                session.delete_instance()

            yield delete_session()
            self.clear_cookie('session')
            self.redirect('/login')



class AdminHandler(BaseHandler):
    @coroutine
    def get(self):

        @in_thread
        def fetch_users():
            u = User.select()
            return u

        users = yield fetch_users()
        return self.render('admin/index.html', users=users)

class AdminUserHandler(BaseHandler):
    def get(self):
        action = self.get_argument('action')

        if action == 'create':
            user = SimpleNamespace()
            setattr(user, 'uuid', 'new')
            setattr(user, 'email', '')

        elif action == 'edit':
            id = self.get_argument('uuid')
            user = User.get(uuid=id)
        else:
            return

        return self.render('admin/user.html', user=user)

    @coroutine
    def post(self):
        action = self.get_argument('action')
        id = self.get_argument('uuid')

        if action == 'create':
            @in_thread
            def create_user():
                u = User.create(
                    email=self.get_argument('email'),
                    password=self.get_argument('password')
                )

                u.save()
                return u

            try:
                user = yield create_user()

            except Exception as ex:
                print("//TODO: Catch invalid argument exception")
                raise ex

        elif action == 'delete':
            @in_thread
            def delete_user():
                id = self.get_argument('uuid')
                u = User.get(uuid=id)
                u.delete_instance()

            yield delete_user()

        elif action == 'edit':
            email = self.get_argument('email')
            passwd = self.get_argument('password')
            confirm = self.get_argument('confirm_password')
            id = self.get_argument('uuid')

            if passwd != '':
                if passwd != confirm:
                    self.error_messages.append(ERR_PASSWORD_CONFIRM_FAILED())

                    user = SimpleNamespace()
                    setattr(user, 'email', email)
                    setattr(user, 'uuid', id)

                    return self.render('admin/user.html', user=user)

                @in_thread
                def update_user():
                    u = User.get(uuid=id)
                    u.email = email
                    u.password = password(passwd)
                    u.save()

                yield update_user()

        self.redirect('/admin')

