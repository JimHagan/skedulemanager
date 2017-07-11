"""
Author: Jim Hagan
Copyright 2017 All rights reserved.
"""
import os
import pytz
import requests
from datetime import datetime, timedelta

requests.adapters.DEFAULT_RETRIES = 3


class SkeduleManager(object):
    def __init__(self)
        self.username = username
        self.pwd = pwd
        self.endpoint = os.environ.get('SK_USERNAME', '')
        self.endpoint = os.environ.get('SK_PWD', '')
        self.endpoint = os.environ.get('SK_ENDPOINT', '')

    def get_skedules(self):
        pass

    def add_or_update_skedule(self):
        pass
