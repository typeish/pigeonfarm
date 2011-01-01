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
        raw_sender_ip = self.request.remote_addr
        sender_ip = IP.get_or_insert(raw_sender_ip)
        
        if not sender_ip.blocked:
            site = self.request.get('site', None)
            sender = self.request.get('sender', None)
            subject = self.request.get('subject', None)
            body = self.request.get('body', None)
            referrer = self.request.referrer
            if not referrer:
                referrer = self.request.referer
        
            site = Site.all().filter('domain =', site).fetch(1)
            if len(site) == 1:
                site = site[0]
            else:
                site = None
        
            if site and sender and subject and body:
                message = Message(site=site, sender=sender, subject=subject, body=body, sender_ip=sender_ip, referrer=referrer)
                message.put()
                if site.dispatch and site.recipients:
                    taskqueue.add(url='/tasks/dispatch/', params={ 'message_id': str(message.key()) })
                result = {'status': 'success'}
                sender_ip.count += 1
            else:
                sender_ip.blocked_count += 1
        else:
            sender_ip.blocked_count += 1

        if not sender_ip.ip:
            sender_ip.ip = raw_sender_ip

        sender_ip.put()
        if not sender_ip.geo and settings.IPINFODB_KEY:
            taskqueue.add(url='/tasks/geolocate/', params={ 'ip_id': str(sender_ip.key()) })

        self.response.headers["Content-Type"] = "application/javascript"
        callback = self.request.get('callback', None)
        if callback and valid_callback.match(callback):
            result = '%s(%s)' % (callback, result)
        self.response.out.write(result)


class MessageBrowser(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        
        context = {
            #'new_messages': Message.all().filter('blocked =', False).order('-received').filter('received >', datetime.now()),
            'old_messages': Message.all().filter('blocked =', False).order('-received').filter('received <=', datetime.now()),
            'signout_url': users.create_logout_url("/"),
            'user': user,
        }
        result = render('messages.html.django', context)
        self.response.out.write(result)

class BlacklistBrowser(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        context = {
            'blacklist': IP.all().filter('blocked =', True),
            'signout_url': users.create_logout_url("/"),
            'user': user,
        }
        result = render('blacklist.html.django', context)
        self.response.out.write(result)

class BlacklistAdd(webapp.RequestHandler):
    def get(self):
        ip_key = self.request.get('ip_key', None)
        if ip_key:
            try:
                ip = db.Get(db.Key(ip_key))
            except:
                pass
            else:
                for m in Message.all().filter('blocked =', False).filter('sender_ip =', ip):
                    m.blocked = True
                    m.put()
                ip.put()
        self.redirect('/')

class SiteBrowser(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        context = {
            'sites': Site.all(),
            'signout_url': users.create_logout_url("/"),
            'user': user,
        }
        result = render('sites.html.django', context)
        self.response.out.write(result)

    def post(self):
        domain = self.request.POST.get('domain', None)

        if domain:
            site = Site.all().filter('domain =', domain).fetch(1)
            if len(site) != 1:
                site = Site(domain=domain)
                site.put()
        self.redirect('/sites/')
        
def main():
    application = webapp.WSGIApplication([
        ('/inbound/', MessageHandler),
        ('/', MessageBrowser),
        ('/blacklist/', BlacklistBrowser),
        ('/blacklist/add', BlacklistAdd),
        ('/sites/', SiteBrowser),
    ], debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
