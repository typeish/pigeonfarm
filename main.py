from django.utils import simplejson as json
from google.appengine.api import users
from google.appengine.api.labs import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from datetime import datetime
from uuid import uuid4

from models import *
import settings

from utils import render

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
                ip = db.get(db.Key(ip_key))
            except:
                pass
            else:
                ip.blocked = True
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
            if len(site) == 0:
                site = Site(domain=domain, access_key=str(uuid4()))
                site.put()
        self.redirect('/sites/')
        
def main():
    application = webapp.WSGIApplication([
        ('/', MessageBrowser),
        ('/blacklist/', BlacklistBrowser),
        ('/blacklist/add', BlacklistAdd),
        ('/sites/', SiteBrowser),
    ], debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
