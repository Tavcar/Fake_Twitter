from handlers.base import BaseHandler
from google.appengine.api import users
from models.user import User
from models.message import Message
from models.follow import Follow
from datetime import datetime
from operator import attrgetter


class HomeHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        c_user = User.query(User.email == user.email()).get()

        if c_user and c_user.handle != None:
            name = c_user.name
            handle = c_user.handle

            t_user = user
            t_list = Message.query(Message.email == c_user.email, Message.deleted == False).fetch()
            sorted_list = sorted(t_list, key=attrgetter("date"), reverse=True)

            params = {"t_list": sorted_list, "user": c_user, "tuser": t_user, "name": name, "handle": handle}
            return self.render_template("home.html", params=params)

        else:
            return self.redirect_to("edit")

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
            message.deleted = True
            message.put()

        if text:
            message = Message(user_name=user_name, email=email, text=text, date=date, userid=userid,
                              user_handle=user_handle)
            message.put()

        return self.redirect_to("home")


class OtherHandler(BaseHandler):
    def get(self, user_id):
        o_user = User.get_by_id(int(user_id))
        name = o_user.name
        handle = o_user.handle
        email = o_user.email
        message_list = Message.query(Message.email == o_user.email, Message.deleted == False).fetch()
        sorted_list = sorted(message_list, key=attrgetter("date"), reverse=True)

        user = users.get_current_user()
        if user:
            u_email = user.email()
            follow_check = Follow.query(Follow.user_id == u_email, Follow.following_id == email).get()

            params = {"list": sorted_list, "user": o_user, "name": name, "handle": handle, "id_user": user_id,
                      "follow_check": follow_check}

            return self.render_template("other.html", params=params)
        else:
            params = {"list": message_list, "user": o_user, "name": name, "handle": handle, "id_user": user_id}

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
        following_list = Follow.query(Follow.user_id == user.email()).fetch()

        if following_list:
            for followers in following_list:
                follow = followers.following_id
                msg_list = Message.query(Message.email == follow, Message.deleted == False).fetch()
                sorted_list = sorted(msg_list, key=attrgetter("date"), reverse=True)

                if msg_list:
                    for message in msg_list:
                        uid = message.userid
                        o_user = User.query(User.user_id == uid).get()
                        params = {"list": sorted_list, "o_user": o_user, "name": name, "handle": handle}

                        return self.render_template("following.html", params=params)
                else:
                    params = {"name": name, "handle": handle}

                    return self.render_template("following.html", params=params)
        else:
            params = {"name": name, "handle": handle}

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
