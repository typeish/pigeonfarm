from google.appengine.api import mail
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import util

from datetime import datetime

import settings

class MessageDispatcher(webapp.RequestHandler):
    def post(self):
        message_key = self.request.get('message_id', None)
        if message_key:
            # Try getting an object using the provided encoded key
            message = db.get(db.Key(message_key))
            email_message = mail.EmailMessage(sender="Pigeon Farm - %s <alecperkins@gmail.com>" % message.site,
                                        subject="PF - %s - %s: %s" % (message.site, message.sender, message.subject))

            email_message.to = message.recipients
            email_message.body = """New message from %s on %s:
            -
            %s
            """ % (message.sender, message.site, message.body)

            email_message.send()
            message.dispatched = datetime.now()
            message.put()

def main():
    application = webapp.WSGIApplication([
        ('/dispatch/', MessageDispatcher)
    ], debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()