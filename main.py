from datetime import datetime
from django.utils import simplejson as json
from google.appengine.api import mail, users
from google.appengine.api.labs import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from models import *
import settings

from utils import render

# https://github.com/simonw/json-time/blob/master/jsontime.py
import re
# Allow 'abc' and 'abc.def' but not '.abc' or 'abc.'
valid_callback = re.compile('^\w+(\.\w+)*$')

class MessageHandler(webapp.RequestHandler):
    def get(self):
        site = self.request.get('site', None)
        sender = self.request.get('sender', None)
        subject = self.request.get('subject', None)
        body = self.request.get('body', None)
        sender_ip = self.request.remote_addr
        referrer = self.request.referrer
        if not referrer:
            referrer = self.request.referer
        
        recipients = settings.RECIPIENTS.get(site, None)
        
        result = {'status': 'failed'}
        if site and sender and subject and body and recipients:
            message = Message(recipients=recipients, site=site, sender=sender, subject=subject, body=body, sender_ip=sender_ip, referrer=referrer)
            message.put()
            # taskqueue.add(url='/dispatch/', params={ 'message_id': str(message.key()) })
            result = {'status': 'success'}
        
        self.response.headers["Content-Type"] = "application/javascript"
        callback = self.request.get('callback', None)
        if callback and valid_callback.match(callback):
            result = '%s(%s)' % (callback, result)
        self.response.out.write(result)


class MessageBrowser(webapp.RequestHandler):
    def get(self):
        if users.is_current_user_admin():
            user = users.get_current_user()
            visit = LogVisit.get_or_insert(user.nickname())
            context = {
                'new_messages': Message.all().order('-received').filter('received >', visit.visit),
                'old_messages': Message.all().order('-received').filter('received <=', visit.visit),
                'signout_url': users.create_logout_url("/"),
                'user': user,
            }
            result = render('messages.html.django', context)
            visit.put()
        else:
            result = ("<a href=\"%s\">login</a>" % users.create_login_url("/"))
        self.response.out.write(result)


def main():
    application = webapp.WSGIApplication([
        ('/inbound/', MessageHandler),
        ('/', MessageBrowser),
    ], debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
