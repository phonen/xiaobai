# -*- coding: utf-8 -*-

import os
import sys
import json
import pymysql
from requests import Session
from requests.utils import default_user_agent
from requests.exceptions import HTTPError, Timeout, TooManyRedirects, RequestException
# import socket
from ssl import SSLError
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

def handle_rest_response(response):
    parseJsonResponse = True
    if parseJsonResponse:
        last_json_response = json.loads(response) if len(response) > 1 else None
        return last_json_response
    else:
        return response

api = 'https://api.coinmarketcap.com/v1/ticker/?limit=0'
session = None  # Session () by default
logger = None  # logging.getLogger(__name__) by default
userAgent = None
userAgents = {
    'chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    'chrome39': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
}
body = None
if body:
    body = body.encode()
last_http_response = None
last_json_response = None
last_response_headers = None
userAgent = default_user_agent()
timeout = 10000  # milliseconds = seconds * 1000
session = session if session else Session()
response = session.request('GET', api, data=body, headers=None, timeout=int(timeout / 1000))
last_http_response = response.text
result = handle_rest_response(last_http_response)
db = pymysql.connect("localhost","root","KeYpZrZx","btc")
cursor = db.cursor()
#cursor.execute("truncate table coinmarket_last")
#db.commit()
for data in result:
    if data['id'] and data['name'] and data['symbol']:
        sql1 = """insert into coins(id,symbol,name) values ('%s','%s','%s') ON DUPLICATE KEY UPDATE id ='%s', symbol='%s', name='%s' """ % (data['id'],data['symbol'],data['name'],data['id'],data['symbol'],data['name'])
        print(sql1)
        try:
            cursor.execute(sql1)
            db.commit()

        except:
            print('error')
            db.rollback()
db.close()



