#!/usr/bin/env python

import httplib2
import logging
log = logging.getLogger(__name__)

from google.appengine.api import memcache
from oauth2client.service_account import ServiceAccountCredentials

import config as cfg

# Handles authentication using Service Account.
def get_Auth():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(cfg.CREDENTIAL_SERVICE, cfg.DEFAULT_SCOPES)
    http = httplib2.Http(memcache, timeout=60)
    #http = httplib2.Http()
    return credentials.authorize(http)
    