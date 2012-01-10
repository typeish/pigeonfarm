from google.appengine.api import mail
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import util

from datetime import datetime

import settings

class MessageDispatchTask(webapp.RequestHandler):
    def post(self):
        message_key = self.request.get('message_id', None)
        if message_key:
            # Try getting an object using the provided encoded key
            message = db.get(db.Key(message_key))
            
            email_recipients = []
            sms_recipients = []
            for r in message.site.recipients:
                if '@' in r:
                    email_recipients.append(r)
                else:
                    sms_recipients.append(r)

            # BUILD EMAIL MESSAGE
            #   The sender property must be a valid address for the app. The
            #   reply-to property is set to the address given by the sender,
            #   allowing for direct replies.
            #
            #   See http://code.google.com/appengine/docs/python/mail/emailmessagefields.html
            #   for more information.
            email_message = mail.EmailMessage(
                sender      = "%s contact form <%s@pigeon-farm.appspotmail.com>" % (message.site.name, message.site.domain),
                subject     = "PF - %s - %s: %s" % (message.site.domain, message.sender, message.subject),
                reply_to    = "%s" % (message.sender,),
            )

            email_message.body = """New message from %s on %s:
            -
            %s
            """ % (message.sender, message.site.domain, message.body)

            for r in email_recipients:
                email_message.to = r
                email_message.send()

            message.dispatched = datetime.now()
            message.put()


class GeolocateTask(webapp.RequestHandler):
    def post(self):
        ip_key = self.request.get('ip_id', None)
        if ip_key:
            # Try getting an object using the provided encoded key
            ip = db.get(db.Key(ip_key))
            ip.geolocate()


def main():
    application = webapp.WSGIApplication([
        ('/tasks/dispatch/', MessageDispatchTask),
        ('/tasks/geolocate/', GeolocateTask)
    ], debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()