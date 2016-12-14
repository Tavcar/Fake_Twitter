import datetime
from handlers.base import BaseHandler
from models.message import Message


class DeleteMessageCron(BaseHandler):
    def get(self):
        deleted_messages = Message.query(Message.deleted == True, Message.updated <
                                         datetime.datetime.now() - datetime.timedelta(days=10)).fetch()
        for message in deleted_messages:
            message.key.delete()