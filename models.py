from google.appengine.ext import db
from datetime import datetime

class BlockedIP(db.Model):
    notes       = db.TextProperty(indexed=False)
    blocked     = db.DateTimeProperty(auto_now_add=True)    # datetime IP blocked
    count       = db.IntegerProperty(indexed=False, default=0)
    ip          = db.StringProperty(indexed=False)

class Message(db.Model):
    """
    A message object received from a remote page.
    
    """
    recipients  = db.ListProperty(str, indexed=False)       # recipient email addresses
    sender      = db.StringProperty(indexed=False)          # sender email address
    sender_ip   = db.StringProperty()                       # sender ip address (for blacklisting)
    referrer    = db.StringProperty(indexed=False)          # sending referrer
    subject     = db.StringProperty(indexed=False)          # email subject
    body        = db.TextProperty(indexed=False)            # message body
    site        = db.StringProperty()                       # domain of source site
    received    = db.DateTimeProperty(auto_now_add=True)    # datetime message received
    dispatched  = db.DateTimeProperty()                     # datetime message dispatched
    blocked     = db.ReferenceProperty(BlockedIP)

class LogVisit(db.Model):
    visit       = db.DateTimeProperty(auto_now=True)
