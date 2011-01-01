from google.appengine.ext import db

from datetime import datetime
from urllib import urlencode
from urllib2 import urlopen

import settings
from django.utils import simplejson as json

class IP(db.Model):
    """
    An IP address. Keeps track of how many messages have come/are coming from the given IP. IPs are automatically geolocated to latitude and longitude coordinates using ipinfodb.com. Optionally, notes about an IP can be added. The IP can be marked as blocked. When blocked, messages from the IP are added to the count, but otherwise ignored and not saved to the datastore.
    """
    notes           = db.TextProperty(indexed=False)            # any notes about the IP address
    added           = db.DateTimeProperty(auto_now_add=True,    # datetime IP added to db
                                     indexed=False)
    blocked         = db.BooleanProperty(default=False)         # datetime IP blocked
    count           = db.IntegerProperty(default=0)             # a running count of messages from the IP while unblocked
    blocked_count   = db.IntegerProperty(default=0)             # a running count of messages from the IP while blocked
    ip              = db.StringProperty(indexed=False)          # the IP address
    geo             = db.GeoPtProperty()                        # the geolocated lat/lon of the IP address
    loc_text        = db.StringProperty(indexed=False)          # the text of the location as 'City, Region, Country (Country Code)' (eg 'Troy, New York, United States (US)')
    
    def geolocate(self):
        """
        Geolocates the IP address using ipinfodb.com.
        
        """

        url = 'http://api.ipinfodb.com/v2/ip_query.php'
        data = {
            'ip': self.ip,
            'output': 'json',
            'timezone': False,
            'key': settings.IPINFODB_KEY
        }
        data = urlencode(data)
        u = urlopen(url + '?' + data)
        response = u.read()
        u.close()
        response = json.loads(response)
        lat = response.get('Latitude',None)
        lon = response.get('Longitude',None)
        if lat:
            lat = float(lat)
        else:
            lat = 0.0
        if lon:
            lon = float(lon)
        else:
            lon = 0.0
        self.geo = db.GeoPt(lat, lon=lon)
        self.loc_text = '%s, %s, %s (%s)' % (response.get('City',''), response.get('RegionName',''), response.get('CountryName',''), response.get('CountryCode',''))
        self.put()


class Site(db.Model):
    """
    A site object used for managing a specific site. Each site is assigned a key which must be provided with the message coming from the site.
    
    (The keys are not intended to be secret, as they have to be provided to the client, nor are they used for any sort of encryption. They are simply something that must be explicitly looked up in order to forge a message.)
    
    """
    name        = db.StringProperty(indexed=False)          # the name of the site (for admin purposes, defaults to domain)
    domain      = db.StringProperty()                       # the bare domain of the site, (eg example.com or www.example.com)
    access_key  = db.StringProperty(indexed=False)          # an arbitrary assigned key for anti-forgery
    recipients  = db.ListProperty(str, indexed=False)       # a list of the assigned recipients
    dispatch    = db.BooleanProperty(default=True, indexed=False)                      # whether or not to dispatch emails

class Message(db.Model):
    """
    A message object received from a remote page.
    
    """
    sender      = db.StringProperty()                       # sender email address
    sender_ip   = db.ReferenceProperty(IP)                  # sender ip address (for blacklisting)
    referrer    = db.StringProperty(indexed=False)          # sending referrer
    subject     = db.StringProperty(indexed=False)          # email subject
    body        = db.TextProperty(indexed=False)            # message body
    site        = db.ReferenceProperty(Site)                # domain of source site
    received    = db.DateTimeProperty(auto_now_add=True)    # datetime message received
    dispatched  = db.DateTimeProperty()                     # datetime message email dispatched
    blocked     = db.BooleanProperty(default=False)         # if the message is from an IP since blocked


class UserSettings(db.Model):
    """
    A settings manager that tracks per-user settings

    """
    last_visit  = db.DateTimeProperty(indexed=False)     # the last time the user visited
    