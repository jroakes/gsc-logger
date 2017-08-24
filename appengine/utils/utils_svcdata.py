#!/usr/bin/env python

import json
import config as cfg

# Pulls data from your service credentials file makes it available as a dictionary.
class ServiceData():
    def __init__(self):
        with open(cfg.CREDENTIAL_SERVICE) as data_file:    
            self.data =  json.load(data_file)
    def __getitem__(self, i):
        return self.data[i]
    def __iter__(self): 
        return self.data.itervalues()