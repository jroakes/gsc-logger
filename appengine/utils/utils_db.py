#!/usr/bin/env python

from google.appengine.ext import ndb
import config as cfg

# Returns a key entity.
def site_key(site):
    return ndb.Key('GSCSites', site)

# Main Cron log class.
class CronLog(ndb.Model):
    gsc_date = ndb.StringProperty(indexed=False)
    count = ndb.IntegerProperty(indexed=False, default=0)
    date = ndb.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def query_log(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key).order(-cls.date)

# Parameters
# site: site url string
# gsc_date: eg. yyyy-mm-dd
def add_entry(site, gsc_date, count):
    
    cronentry = CronLog( parent=site_key(site) )
    cronentry.gsc_date = gsc_date
    cronentry.count = count
    cronentry.put()

# Deletes all entries from the database
def delete_entries():
    return ndb.delete_multi(CronLog.query().fetch(keys_only=True))


# Parameters
# site: site url string
# Returns
# gsc-style date or never string
def last_date(site):
    
    cronentry = CronLog.query_log(site_key(site)).fetch(1)
    
    if len(cronentry) > 0:
        return cronentry[0].gsc_date
    else:
        return 'Never'
    
def last_count(site):
    
    cronentry = CronLog.query_log(site_key(site)).fetch(1)
    
    if len(cronentry) > 0:
        return cronentry[0].count
    else:
        return 0
    
    