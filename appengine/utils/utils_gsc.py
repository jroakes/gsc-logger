#!/usr/bin/env python

import time
from datetime import datetime, timedelta
import pytz

import httplib2
import logging
import json
import googleapiclient.discovery as discovery
from googleapiclient.errors import HttpError

import config as cfg
import utils.utils_auth as auth
import utils.utils_bigq as bigq
import utils.utils_db as db

log = logging.getLogger(__name__)

# Decorator to provide rate limiting to GSC function.
# Credit: https://github.com/stephan765/Google-Search-Console-bulk-query/blob/master/search_console_query.py
def rate_limit(max_per_minute):
    """
    Decorator function to prevent more than x calls per minute of any function
    Args:
        max_per_minute. Numeric type.
        The maximum number of times the function should run per minute.
    """
    min_interval = 60.0 / float(max_per_minute)
    def decorate(func):
        last_time_called = [0.0]
        def rate_limited_function(*args, **kwargs):
            elapsed = time.clock() - last_time_called[0]
            wait_for = min_interval - elapsed
            if wait_for > 0:
                time.sleep(wait_for)
            ret = func(*args, **kwargs)
            last_time_called[0] = time.clock()
            return ret
        return rate_limited_function
    return decorate

# Returns the GCS format date based on OFFSET_DATE specified in config.py
def get_offset_date(days):
    return (datetime.now(pytz.timezone(cfg.GSC_TIMEZONE)) - timedelta(days=days)).strftime("%Y-%m-%d")

# Return a list of unvisited dates for the specified site.
def dates_list(site):
    return (get_offset_date(days) for days in range(cfg.OFFSET_START_DATE, cfg.OFFSET_END_DATE) \
           if get_offset_date(days) > db.last_date(site) or db.last_date(site) == 'Never')

# Returns the GSC service
def get_gsc_service():

    service = discovery.build('webmasters', 'v3', http=auth.get_Auth())
    return service

# Lists all sites that are available to you based on your serice email address.
def list_sites():

    data = []

    allowed = ['siteOwner','siteFullUser']

    service = get_gsc_service()
    site_list = service.sites().list().execute()

    log.info(site_list)
    if site_list and 'siteEntry' in site_list:
        for site in site_list['siteEntry']:
            if site['permissionLevel'] in allowed:
                data.append(site['siteUrl'])

    return data

#Main request to GSC
# Credit: https://github.com/stephan765/Google-Search-Console-bulk-query/blob/master/search_console_query.py
@rate_limit(400)
def execute_request(service, property_uri, request, max_retries=5, wait_interval=4,
                    retry_errors=(503, 500)):
    """
    Executes a searchanalytics request.
    Args:
        service: The webmasters service object/client to use for execution.
        property_uri: Matches the URI in Google Search Console.
        request: The request to be executed.
        max_retries. Optional. Sets the maximum number of retry attempts.
        wait_interval. Optional. Sets the number of seconds to wait between each retry attempt.
        retry_errors. Optional. Retry the request whenever these error codes are encountered.
    Returns:
        An array of response rows.
    """

    response = None
    retries = 0
    while retries <= max_retries:
        try:
            response = service.searchanalytics().query(siteUrl=property_uri, body=request).execute()
        except HttpError as err:
            decoded_error_body = err.content.decode('utf-8')
            json_error = json.loads(decoded_error_body)
            log.error(decoded_error_body)
            if json_error['error']['code'] in retry_errors:
                time.sleep(wait_interval)
                retries += 1
                continue
        break

    return response

# Given a site url string, loads all data for a particular date to BiqQuery
def load_site_data(site, date):

    data = None
    loaded = False

    query = cfg.GSC_QUERY

    query['startDate'] = date
    query['endDate']   = date

    service = get_gsc_service()

    while True:

        data = execute_request(service, site, query)
        if data and 'rows' in data:
            rows = data['rows']
            numRows = len(rows)
            rowsSent = 0

            try:
                result = bigq.stream_row_to_bigquery(site, rows)
                log.info('Added {0} rows to {1}'.format(numRows, site))
                rowsSent += numRows
                loaded = True

                if numRows == 5000:
                    query['startRow'] = int(rowsSent + 1)
                    continue
                else:
                    if numRows and numRows > 0:
                        db.add_entry(site, date, rowsSent)
                    break

            except HttpError as e:
                log.error("Stream to Bigquery error. ", e.content)
                break

        else:
            break

    if loaded:
        log.info('Data loaded for date {0} and site {1}'.format(date, site))
    else:
        log.error('Could not load data for date {0} and site {1}'.format(date, site))

    return loaded

# Main Cron script.
def run_gsc_cron():

    sites = list_sites()
    error = False
    message = ""

    try:
        #Audit Sites
        audit = bigq.audit_tables(sites)

        log.info('Tables Audited')

        #load site data to BigQuery
        for site in sites:
            for date in dates_list(site):

                loaded = load_site_data(site, date)

        message = str(sites)

    except HttpError as e:
        log.error("GSC Cron Error, {0}".format(e.content))
        message = "GSC Cron Error, {0}".format(e.content)
        error = True

    return error, message
