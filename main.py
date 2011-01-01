from datetime import datetime
from django.utils import simplejson as json
from google.appengine.api import users
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
        result = {'status': 'failed'}
        sender_ip = self.request.remote_addr
        blocked_ip = BlockedIP.get_by_key_name(sender_ip)
        if not blocked_ip:
            site = self.request.get('site', None)
            sender = self.request.get('sender', None)
            subject = self.request.get('subject', None)
            body = self.request.get('body', None)
            referrer = self.request.referrer
            if not referrer:
                referrer = self.request.referer
        
            recipients = settings.RECIPIENTS.get(site, None)
        
            if site and sender and subject and body and recipients:
                message = Message(recipients=recipients, site=site, sender=sender, subject=subject, body=body, sender_ip=sender_ip, referrer=referrer)
                message.put()
                if recipients and len(recipients) > 0:
                    taskqueue.add(url='/dispatch/', params={ 'message_id': str(message.key()) })
                result = {'status': 'success'}
        else:
            blocked_ip.count += 1
            blocked_ip.put()

        self.response.headers["Content-Type"] = "application/javascript"
        callback = self.request.get('callback', None)
        if callback and valid_callback.match(callback):
            result = '%s(%s)' % (callback, result)
        self.response.out.write(result)


class MessageBrowser(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        visit = LogVisit.get_or_insert(user.nickname())
        context = {
            'new_messages': Message.all().filter('blocked =', None).order('-received').filter('received >', visit.visit),
            'old_messages': Message.all().filter('blocked =', None).order('-received').filter('received <=', visit.visit),
            'signout_url': users.create_logout_url("/"),
            'user': user,
        }
        result = render('messages.html.django', context)
        visit.put()
        self.response.out.write(result)

class BlacklistBrowser(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        context = {
            'blacklist': BlockedIP.all(),
            'signout_url': users.create_logout_url("/"),
            'user': user,
        }
        result = render('blacklist.html.django', context)
        self.response.out.write(result)

class BlacklistAdd(webapp.RequestHandler):
    def get(self):
        ip = self.request.get('ip', None)
        if ip:
            blocked_ip = BlockedIP.get_or_insert(ip, ip=ip)
            for m in Message.all().filter('blocked =', None).filter('sender_ip =', ip):
                m.blocked = blocked_ip
                m.put()
                blocked_ip.count += 1
            blocked_ip.put()
        self.redirect("/")

def main():
    application = webapp.WSGIApplication([
        ('/inbound/', MessageHandler),
        ('/', MessageBrowser),
        ('/blacklist/', BlacklistBrowser),
        ('/blacklist/add', BlacklistAdd),
    ], debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
