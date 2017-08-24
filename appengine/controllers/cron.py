#!/usr/bin/env python

import webapp2
import json
import config as cfg
import utils.utils_gsc as gsc

class CronHandler(webapp2.RequestHandler):

    def get(self):
        
        if not cfg.ALLOW_OPEN_CRON and self.request.headers.get('X-AppEngine-Cron') is None:
            error = True
            content = 'Access Denied'
        else:
            error , content = gsc.run_gsc_cron()        
            
        self.response.headers['Content-Type'] = 'application/json'
        
        if error:
            self.response.write(json.dumps({"status": "503", "data": content}))
        else:
            self.response.write(json.dumps({"status": "200", "data": content}))