import webapp2
from crons.delete_tweets import DeleteMessageCron
from handlers.base import BaseHandler, MainHandler, CookieAlertHandler
from handlers.messages import HomeHandler, OtherHandler, FollowingHandler
from handlers.users import EditHandler, ConfirmNameHandler, SearchResultsHandler


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="main-page"),
    webapp2.Route('/set-cookie', CookieAlertHandler, name="set-cookie"),

    webapp2.Route('/home', HomeHandler, name="home"),
    webapp2.Route('/other/<user_id:\d+>', OtherHandler, name="other"),
    webapp2.Route('/following', FollowingHandler, name="following"),

    webapp2.Route('/edit', EditHandler, name="edit"),
    webapp2.Route('/confirm', ConfirmNameHandler, name="confirm"),
    webapp2.Route('/results', SearchResultsHandler, name="results"),

    webapp2.Route('/cron/delete-message', DeleteMessageCron, name="delete-message-cron"),
], debug=True)
