# -*- coding: utf-8 -*-

import os
from google.appengine.ext.webapp import template
import settings

from django.utils import simplejson as json

def render(template_name, context={}):
    path = os.path.join(settings.TEMPLATE_DIRECTORY, template_name)
    return template.render(path, context)


def parse_recipient_list(recipients):
	if recipients:
		recipients = recipients.replace(' ','')
		return recipients.split(',')
	return []