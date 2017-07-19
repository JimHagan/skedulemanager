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

    def get_profile(self, user_name):
        """
            Get an existing user profile given a user name
	"""
	get_profile_url = '{0}profiles/{1}'.format(self.endpoint, user_name)
        response = requests.get(get_profile_url, headers=self.auth_headers)
        return response

    def get_skedule(self, sk_id):
	"""
	    Get an existing skedule given a skedule id
	"""
        get_skedule_url = '{0}skedules/{1}'.format(self.endpoint, sk_id)
	response = requests.get(get_skedule_url, headers=self.auth_headers)
        return response

    def post_event_for_skedule(self, sk_id, event_content):
	"""
	    Posts a new event
	    Minimal sample data: {"title":"My new event", "starts_on":"06/12/2017 15:00"}
	"""
	post_event_url = '{0}skedules/{1}/events/'.format(self.endpoint, sk_id)
        response = requests.post(post_event_url, data=json.dumps(event_content), headers=self.auth_headers)
        return response

    def patch_event(self, event_id, patch_data):
	"""
	    Patch an existing event
	    {"description":"Added a description"}
	"""
	patch_event_url = '{0}events/{1}/'.format(self.endpoint, event_id)
        response = requests.patch(patch_event_url, data=json.dumps(patch_data), headers=self.auth_headers)
        return response

    def get_single_event(self, sk_id, event_id):
	"""
	   Get a single event given a skedule id and event id
	"""
        get_event_url = '{0}skedules/{1}/events/{2}/'.format(self.endpoint, sk_id, event_id)
	print get_event_url
	response = requests.get(get_event_url, headers=self.auth_headers)
        return response

    def get_events_for_skedule(self, sk_id):
        """
            Get all events for a given skedule
	"""
	get_events_url = '{0}skedules/{1}/events'.format(self.endpoint, sk_id)
        response = requests.get(get_events_url, headers=self.auth_headers)
	return response

    def post_new_skedule(self, skedule_content):
        """
            Add a new skedule
            Minimal sample data: {"title":"My new skedule"}
        """
        post_skedule_url = '{0}profiles/{1}/skedules/'.format(self.endpoint, self.username)
        response =  requests.post(post_skedule_url, data=json.dumps(skedule_content), headers=self.auth_headers)        
	return response

    def patch_schedule(self, sk_id, patch_data):
	"""
	    Patch an existing skedule
	    Minimal sample data: {"is_public":true}
	"""
        patch_skedule_url = '{0}skedules/{1}'.format(self.endpoint, sk_id)
        response = requests.patch(patch_skedule_url, data=patch_data, headers=self.auth_headers)
        return response

if __name__ == "__main__":
    skmgr = SkeduleManager()
    #new_skedule = skmgr.post_new_skedule({'title': 'PRO Sports Skedule'}).json()
