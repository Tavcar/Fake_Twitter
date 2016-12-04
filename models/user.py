from google.appengine.ext import ndb


class User(ndb.Model):
    user_id = ndb.StringProperty()
    name = ndb.StringProperty()
    handle = ndb.StringProperty()
    email = ndb.StringProperty()
