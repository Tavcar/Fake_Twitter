from google.appengine.ext import ndb


class Message(ndb.Model):
    userid = ndb.StringProperty()
    email = ndb.StringProperty()
    user_name = ndb.StringProperty()
    user_handle = ndb.StringProperty()
    date = ndb.StringProperty()
    text = ndb.StringProperty()

    @classmethod
    def create(cls, user_name, email, text, date, userid, user_handle):
        message = cls(user_name=user_name, email=email, text=text, date=date, userid=userid, user_handle=user_handle)
        message.put()
        return message
