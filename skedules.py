"""
Author: Jim Hagan
Copyright 2017 All rights reserved.
"""
from config import ENV
import os
import pickle
import pytz
import requests
from datetime import datetime, timedelta

requests.adapters.DEFAULT_RETRIES = 3


class SkeduleManager(object):
    def _authenticate(self):
        self.api_token = ''

    def __init__(self):
        self.username = ENV.get('SK_USERNAME', '')
        self.pwd = ENV.get('SK_PWD', '')
        self.endpoint = ENV.get('SK_ENDPOINT', '')
        self._authenticate()


    def get_skedules(self):
        pass

    def add_or_update_skedule(self):
        pass


if __name__ == "__main__":
    skmgr = SkeduleManager()
    print skmgr.username
    print skmgr.pwd
    print skmgr.endpoint    
