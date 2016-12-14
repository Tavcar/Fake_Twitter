#!/usr/bin/env python
import os
import jinja2
from google.appengine.api import users
from models.message import Message
from models.user import User
from models.follow import Follow
from google.appengine.api import memcache
import uuid
import webapp2


template_dir = os.path.join(os.path.dirname(__file__), "../templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}

        template = jinja_env.get_template(view_filename)
        user = users.get_current_user()
        params["user"] = user

        cookie_law = self.request.cookies.get("cookie_law")
        if cookie_law:
            params["cookies"] = True

        if user:
            logiran = True
            params["logout_url"] = users.create_logout_url('/')
            params["logiran"] = logiran

            t_user = User.query(User.email == user.email()).get()
            if t_user:
                pass
            else:
                t_user = User(email=user.email(), handle=None, name=None)
                t_user.put()
        else:
            logiran = False
            params["login_url"] = users.create_login_url('/home')
            params["logiran"] = logiran

        csrf_token = str(uuid.uuid4())
        memcache.add(key=csrf_token, value=True, time=600)

        params["csrf_token"] = csrf_token

        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        params = {"user": user}

        return self.render_template("landing_page.html", params=params)


class CookieAlertHandler(BaseHandler):
    def post(self):
        self.response.set_cookie(key="cookie_law", value="accepted")
        return self.redirect_to("main-page")
