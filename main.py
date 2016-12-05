#!/usr/bin/env python
import os
import jinja2
import webapp2
from google.appengine.api import users
from datetime import datetime
from operator import attrgetter
from models.message import Message
from models.user import User
from models.follow import Follow


template_dir = os.path.join(os.path.dirname(__file__), "templates")
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

        if user:
            logiran = True
            logout_url = users.create_logout_url('/')
            params["logout_url"] = logout_url
            params["logiran"] = logiran

            t_user = User.query(User.email == user.email()).get()
            if t_user:
                return self.response.out.write(template.render(params))
            else:
                t_user = User(email=user.email())
                t_user.put()
                return self.response.out.write(template.render(params))
        else:
            logiran = False
            login_url = users.create_login_url('/home')
            params["login_url"] = login_url
            params["logiran"] = logiran

            return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        params = {"user": user}

        return self.render_template("landing_page.html", params=params)


class HomeHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        c_user = User.query(User.email == user.email()).get()

        if c_user:
            name = c_user.name
            handle = c_user.handle
            email = c_user.email

            t_user = user
            t_list = Message.query(Message.email == c_user.email).fetch()
            sorted_list = sorted(t_list, key=attrgetter("date"), reverse=True)
            params = {"t_list": sorted_list, "user": c_user, "tuser": t_user, "name": name, "handle": handle,
                      "email": email}
            return self.render_template("home.html", params=params)
        else:
            return self.redirect('/edit')

    def post(self):
        user = users.get_current_user()
        t_user = User.query(User.email == user.email()).get()

        email = user.email()
        userid = user.user_id()
        user_name = t_user.name
        user_handle = t_user.handle
        date = datetime.now().strftime("%d-%m-%Y at %H:%M:%S")
        text = self.request.get("text")
        delete = self.request.get("delete")

        if delete:
            message = Message.get_by_id(int(delete))
            message.key.delete()
            return self.redirect_to("home")

        if text:
            message = Message(user_name=user_name, email=email, text=text, date=date, userid=userid,
                              user_handle=user_handle)
            message.put()
            return self.redirect_to("home")

        else:
            return self.redirect_to("home")


class EditHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        t_user = User.query(User.email == user.email()).get()
        params = {"t_user": t_user}

        return self.render_template("edit.html", params=params)

    def post(self):
        name = self.request.get("name")
        handle = self.request.get("handle")

        user = users.get_current_user()
        t_user = User.query(User.email == user.email()).get()

        if User.query(User.handle == handle).get():
            warning = "This handle is already taken."
            params = {"warning": warning, "t_user": t_user}
            return self.render_template("edit.html", params=params)
        else:
            t_user.user_id = user.user_id()
            t_user.name = name
            t_user.handle = handle
            t_user.put()
            return self.redirect('/home')
            #return self.redirect_to("home")


class OtherHandler(BaseHandler):
    def get(self, user_id):
        o_user = User.get_by_id(int(user_id))
        name = o_user.name
        handle = o_user.handle
        email = o_user.email
        message_list = Message.query(Message.email == o_user.email).fetch()

        user = users.get_current_user()
        if user:
            u_email = user.email()
            follow_check = Follow.query(Follow.user_id == u_email, Follow.following_id == email).get()

            params = {"list": message_list, "user": o_user, "name": name, "handle": handle, "email": email,
                      "id_user": user_id, "follow_check": follow_check}

            return self.render_template("other.html", params=params)
        else:
            params = {"list": message_list, "user": o_user, "name": name, "handle": handle, "email": email,
                      "id_user": user_id}
            return self.render_template("other.html", params=params)

    def post(self, user_id):
        user = users.get_current_user()
        o_user = User.get_by_id(int(user_id))
        u_email = user.email()
        o_email = o_user.email
        follow_user = self.request.get("follow")

        if follow_user == "follow":
            follow = Follow(user_id=u_email, following_id=o_email)
            follow.put()
            return self.redirect('/other/' + str(user_id))
        else:
            following = Follow.query(Follow.user_id == u_email, Follow.following_id == o_email).get()
            following.key.delete()

            return self.redirect('/other/' + str(user_id))


class FollowingHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        c_user = User.query(User.email == user.email()).get()
        name = c_user.name
        handle = c_user.handle
        email = c_user.email
        following_list = Follow.query(Follow.user_id == user.email()).fetch()

        if following_list:
            for followers in following_list:
                follow = followers.following_id
                msg_list = Message.query(Message.email == follow).fetch()

                if msg_list:
                    for message in msg_list:
                        uid = message.userid
                        o_user = User.query(User.user_id == uid).get()
                        params = {"list": msg_list, "o_user": o_user, "name": name, "handle": handle, "email": email}
                        return self.render_template("following.html", params=params)
                else:
                    params = {"name": name, "handle": handle, "email": email}
                    return self.render_template("following.html", params=params)
        else:
            params = {"name": name, "handle": handle, "email": email}
            return self.render_template("following.html", params=params)

    def post(self):
        user = users.get_current_user()
        t_user = User.query(User.email == user.email()).get()
        email = user.email()
        userid = user.user_id()
        user_name = t_user.name
        user_handle = t_user.handle
        date = datetime.now().strftime("%d-%m-%Y at %H:%M:%S")
        text = self.request.get("text")

        if text:
            message = Message(user_name=user_name, email=email, text=text, date=date, userid=userid,
                              user_handle=user_handle)
            message.put()
            return self.redirect_to("following")
        else:
            return self.redirect_to("following")


class SearchResultsHandler(BaseHandler):
    def get(self):
        return self.render_template("results.html")

    def post(self):
        search = self.request.get("search")
        user = users.get_current_user()
        if user:
            t_user = User.query(User.email == user.email()).get()

            if search:
                users_list = User.query().fetch()
                results1 = [i for i in users_list if search in i.name and i.handle != t_user.handle]
                results2 = [i for i in users_list if search in i.handle and i.handle != t_user.handle]
                params = {"results1": results1, "results2": results2}
                return self.render_template("results.html", params=params)
        else:
            if search:
                users_list = User.query().fetch()
                results1 = [i for i in users_list if search in i.name]
                results2 = [i for i in users_list if search in i.handle]
                params = {"results1": results1, "results2": results2}
                return self.render_template("results.html", params=params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="main-page"),
    webapp2.Route('/home', HomeHandler, name="home"),
    webapp2.Route('/other/<user_id:\d+>', OtherHandler, name="other"),
    webapp2.Route('/edit', EditHandler, name="edit"),
    webapp2.Route('/following', FollowingHandler, name="following"),
    webapp2.Route('/results', SearchResultsHandler, name="results"),
], debug=True)
