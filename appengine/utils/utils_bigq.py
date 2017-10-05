#!/usr/bin/env python

import json
import uuid
import re, string
import pytz
from datetime import datetime, timedelta


import googleapiclient.discovery as discovery
from googleapiclient.errors import HttpError

import config as cfg

import utils.utils_auth as auth
from utils.utils_svcdata import ServiceData
svcdata = ServiceData() 

import logging
log = logging.getLogger(__name__)


# Returns the partition format date based on OFFSET_DATE specified in config.py
def get_offset_date():
    return (datetime.now(pytz.timezone(cfg.GSC_TIMEZONE)) - timedelta(days=cfg.OFFSET_DATE)).strftime("%Y%m%d")

# Gets the BigQuery Service   
def get_bq_service():

    service = discovery.build('bigquery', 'v2', http=auth.get_Auth())
    return service

# Creates a BigQuery-safe table id
def convert_table_id(url):
    pattern = re.compile('[\W_]+')
    return pattern.sub('_', url).lower()

# Creates a Friendly table name based on url and config setting.
def convert_table_name(url):
    return cfg.TABLE_FRIENDLY_FRONT + " " + str(url)



# Checks if a dataset for this project has been created.
def is_dataset_set():
    

    try:
        service = get_bq_service()
        dataset = service.datasets().get(
            projectId=svcdata['project_id'], datasetId=cfg.DATASET_ID).execute()
    except HttpError:
        return False

    return True

# Creates BigQuery dataset
def create_dataset():

    try:
        service = get_bq_service()
        datasets = service.datasets()
        dataset_data = {
                        "datasetReference": {
                            "datasetId": cfg.DATASET_ID,
                            "projectId": svcdata['project_id']
                                            }
                       }

        response = datasets.insert(projectId=svcdata['project_id'],body=dataset_data).execute()

        return response
    
    except HttpError as e:
        log.error(
            'Cannot create dataset {0}, {1}'.format(cfg.DATASET_ID, e))
        
        return {}

# Creates a BigQuery table
def create_table(table,name):

    body = {
        'schema': {'fields': cfg.TABLE_SCHEMA},
        'friendlyName' : name,
        'tableReference': {
            'tableId': table,
            'projectId': svcdata['project_id'],
            'datasetId': cfg.DATASET_ID
        },
        'timePartitioning': {
            'type': 'DAY'
        }
    }
        
    try:
        service = get_bq_service()
        table = service.tables().insert(
            projectId=svcdata['project_id'],
            datasetId=cfg.DATASET_ID,
            body=body
        ).execute()

        return table
    
    except HttpError as e:
        log.error(('Cannot create table {0}.{1}\n'
                      'Http Error: {2}').format(cfg.DATASET_ID, table, e.content))

        return False

# Deletes a BiqQuery table
def deleteTable(table):
    try:
        service = get_bq_service()
        result =  service.tables().delete(projectId=svcdata['project_id'], datasetId=cfg.DATASET_ID, tableId=tableId).execute()
        return result
    except HttpError as e:
        log.error(('Cannot delete table {0}.{1}\n'
                      'Http Error: {2}').format(cfg.DATASET_ID, table, e.content))
        return False
    
# Returns list of all tables created in BiqQuery   
def listTables():

    try:
        service = get_bq_service()
        result = service.tables().list(projectId=svcdata['project_id'], datasetId=cfg.DATASET_ID).execute()
        if 'tables' in result:
            return result["tables"]
        else:
            return []
    except HttpError as e:
        log.error(('Cannot list tables {0}\n'
                      'Http Error: {1}').format(cfg.DATASET_ID, e.content))
        return []

# Creates or deletes tables based on Service credential access. Also creates dataset if not already created.
def audit_tables(sites):
    
    if not is_dataset_set():
        create_dataset()
        
    if not is_dataset_set():
        log.error('Could not create dataset.')
        return False
    
    site_ids = list(map(convert_table_id, sites))
    site_names = list(map(convert_table_name, sites))
    
    tables = listTables()
    
    table_ids = []
    new_tables = []
    remove_tables = []
    
    for table in tables:
        table_ids.append(table['tableReference']['tableId'])
    
    new_tables = [x for x in site_ids if x not in table_ids]

    for t in new_tables:
        n = site_names[site_ids.index(t)]
        create_table(t,n)
        
    if cfg.AUTO_REMOVE:  
        remove_tables = [x for x in table_ids if x not in site_ids]
        for t in remove_tables:
            deleteTable(t)
        
    log.info(('Added {0} tables and deleted {1} tables.').format(str(len(new_tables)),str(len(remove_tables))))
    
    return True
        
    

# Streams row data to Biqquery
def stream_row_to_bigquery(site, rows):
    
    insert_all_data = {
        'rows': transform_rows(rows)
    }
    partition_date = get_offset_date()
    service = get_bq_service()
    result =  service.tabledata().insertAll(
        projectId=svcdata['project_id'],
        datasetId=cfg.DATASET_ID,
        tableId=convert_table_id(site)+ '$' + partition_date,
        body=insert_all_data).execute(num_retries=cfg.STREAM_RETRIES)
        
    log.info(json.dumps(result))
    
    return result


# Takes rows in GSC API format and transforms to BiqQuery readable data.     
def transform_rows(rows):
    #In: Raw data response from GSC
    data =[]
    
    for row in rows:
        
        try: 
            item = {}
            item['insertId'] = str(uuid.uuid4())
            item['json'] = {
                            'query' : row['keys'][0],
                            'date' : row['keys'][1],
                            'page' : row['keys'][2],
                            'device' : row['keys'][3],
                            'impressions' : row['impressions'],
                            'clicks' : row['clicks'],
                            'ctr' : row['ctr'],
                            'position' : row['position']
                            }
            data.append(item)
            
        except IndexError as e:
            log.error(('Error creating rows for Bigquery. {0}').format(e.content))
            
            
    return data


        
