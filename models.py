from google.appengine.ext import db
from datetime import datetime

class Message(db.Expando):
    """
    A message object received from a remote page.
    
    """
    recipients = db.ListProperty(str, indexed=False)    # recipient email addresses
    sender = db.StringProperty()                        # sender email address
    sender_ip = db.StringProperty()                     # sender ip address (for blacklisting)
    referrer = db.StringProperty(indexed=False)         # sending referrer
    subject = db.StringProperty(indexed=False)          # email subject
    body = db.TextProperty(indexed=False)               # message body
    site = db.StringProperty()                          # domain of source site
    received = db.DateTimeProperty(auto_now_add=True)   # datetime message received
    dispatched = db.DateTimeProperty()                  # datetime message dispatched

class BlockedIP(db.Model):
    ip = db.StringProperty()
    notes = db.TextProperty(indexed=False)

class LogVisit(db.Model):
    visit = db.DateTimeProperty(auto_now=True)