from handlers.base import BaseHandler
from google.appengine.api import users
from models.user import User


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
            return self.redirect('/confirm')


class ConfirmNameHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        t_user = User.query(User.email == user.email()).get()
        params = {"t_user": t_user}

        return self.render_template("confirm_name.html", params=params)


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