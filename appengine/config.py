#!/usr/bin/env python

# Path to your service credentials json file.
CREDENTIAL_SERVICE = "credentials/credentials_service.json"

# Your default scopes for GAE. Currently only BQ and GSC
DEFAULT_SCOPES = ["https://www.googleapis.com/auth/bigquery", "https://www.googleapis.com/auth/webmasters.readonly"]

# Unique ID for your dataset.
DATASET_ID = 'gsc_logger_sites'

# Since GCS data is dated, specify the offset from today.
OFFSET_DATE = 7

# Should we auto remove DBs if we no longer have access.
# Careful:  Could lose data if you accidentally lose connection.
# Databases can be removed manually at: https://bigquery.cloud.google.com/queries/gsc-logger 
AUTO_REMOVE = False

# Schema used to build the tables.  If you change the data pulled from GSC, you must change this.
TABLE_SCHEMA = [
                    {"type": "DATE", "name": "date"},
                    {"type": "STRING", "name": "query"},
                    {"type": "STRING", "name": "page"},
                    {"type": "STRING", "name": "device"},
                    {"type": "INTEGER", "name": "clicks"},
                    {"type": "INTEGER", "name": "impressions"}, 
                    {"type": "FLOAT", "name": "ctr"}, 
                    {"type": "FLOAT", "name": "position"}
                ]

# Friendly name prefix for tables.
TABLE_FRIENDLY_FRONT = "GSC Logger:"

# How many retries to stream data into BigQuery
STREAM_RETRIES = 5

# Whether the /cron/ path can be called publicly from the web. Should be False after testing.
ALLOW_OPEN_CRON = True

# Hides Homepage data if true.
HIDE_HOMEPAGE = False

# Set Timezone ('US/Eastern', 'US/Central', 'US/Pacific')
GSC_TIMEZONE = 'US/Eastern'

# Base query for GSC.  startDate and endDate are replaced upon call.
GSC_QUERY = {
                 "startDate": "2017-07-01",
                 "endDate": "2017-07-31",
                 "dimensions": [
                  "query",
                  "date",
                  "page",
                  "device"
                 ],
                 "dimensionFilterGroups": [
                  {
                   "filters": [
                    {
                     "dimension": "country",
                     "expression": "usa"
                    }
                   ]
                  }
                 ],
                 "rowLimit": 5000
                }

