from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import util

from datetime import datetime

import settings

class MessageDispatcher(webapp.RequestHandler):
    def post(self):
        message_key = self.request.get('message_id', None)
        if message_key:
            try:
                # Try getting an object using the provided encoded key
                message = db.get(db.Key(message_key))
            except:
                # Either :message_key was not an encoded Key, or the Key was invalid
                pass
            else:
                email_message = mail.EmailMessage(sender="Pigeon Farm <alecperkins@gmail.com>",
                                            subject="PF, %s: %s" % (message.site, message.subject))

                email_message.to = message.recipients[0]
                email_message.body = message.body

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