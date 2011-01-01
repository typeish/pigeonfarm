from django.utils import simplejson as json
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

def main():
    application = webapp.WSGIApplication([
        ('/inbound/', MessageHandler),
    ], debug=settings.DEBUG)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
