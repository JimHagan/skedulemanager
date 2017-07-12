"""
Author: Jim Hagan
Copyright 2017 All rights reserved.
"""
from config import ENV
import json
import os
import pickle
import pytz
import requests
from datetime import datetime, timedelta

requests.adapters.DEFAULT_RETRIES = 3


class SkeduleManager(object):
    def _authenticate(self):
        signin_url = '{0}members/signin/'.format(self.endpoint) 
	signin_data = {"username": self.username,"passwd": self.pwd}
	response = requests.post(signin_url, data=json.dumps(signin_data))
	self.api_token = response.json()['data']['token']
        self.auth_headers = {"Authorization":"Bearer {0}".format(self.api_token)}
	return response
    def __init__(self):
        self.username = ENV.get('SK_USERNAME', '')
        self.pwd = ENV.get('SK_PWD', '')
        self.endpoint = ENV.get('SK_ENDPOINT', '')
        self._authenticate()


    def get_skedules(self):
        pass

    def post_new_skedule(self, skedule_content):
        post_skedule_url = '{0}profiles/{1}/skedules/'.format(self.endpoint, self.username)
        response =  requests.post(post_skedule_url, data=json.dumps(skedule_content), headers=self.auth_headers)        
	print response
	return response

if __name__ == "__main__":
    skmgr = SkeduleManager()
    print skmgr.username
    print skmgr.pwd
    print skmgr.endpoint
    print skmgr.api_token 
    skmgr.post_new_skedule({'title': 'PRO Sports Skedule'})   
