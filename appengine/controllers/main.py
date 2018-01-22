#!/usr/bin/env python

import sys
sys.path.append("./lib")

import os
import httplib2
import webapp2
from googleapiclient.errors import HttpError

import logging
log = logging.getLogger(__name__)

import config as cfg
import utils.utils_gsc as gsc
import utils.utils_db as db

from utils.utils_svcdata import ServiceData
svcdata = ServiceData()

from controllers.cron import CronHandler
from controllers.base import BaseHandler


def check_credentials():
    return os.path.isfile(cfg.CREDENTIAL_SERVICE)

# Handle / Requests
class MainHandler(BaseHandler):

  def get(self):

    sites = None
    sitelist = []

    reset = self.request.get('reset','0')

    if reset == '1':
        db.delete_entries()
        message = "Cron database deleted. <a href='/'>Refresh page</a>."
    elif not check_credentials():
        message = "Upload service credentials JSON from Google App Engine and update filename in config.py file."
    elif cfg.HIDE_HOMEPAGE:
        message = "Nothing to see here."
    else:
        try:
            message = "Add <strong>{0}</strong> to each Google Search Console account that you want to manage.".format(svcdata['client_email'])
            sites = gsc.list_sites()
            for site in sites:
                sitelist.append(site + " (Last Save: " + db.last_date(site) + " --- " + str(db.last_count(site)) + " rows)" )

        except HttpError as e:
            log.error("GSC Error, {0} ".format(e.content))
            message = "GSC Error, {0}. Check Log. ".format(e.content)

    variables = {
        'message': message,
        'sites': sitelist
        }

    self.render_response('root.html', **variables)



app = webapp2.WSGIApplication(
    [
     (r'/', MainHandler),
     (r'/cron/', CronHandler)
    ],
    debug=False)

