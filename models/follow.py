from google.appengine.ext import ndb


class Follow(ndb.Model):
    user_id = ndb.StringProperty()  # ndb.KeyProperty(kind=User)   ndb.IntegerProperty()
    following_id = ndb.StringProperty()  # ndb.KeyProperty(kind=User)

