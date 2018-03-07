# -*- coding: utf-8 -*-

import os
import sys
import json
from flask import Flask,request
from requests import Session
from requests.utils import default_user_agent
from requests.exceptions import HTTPError, Timeout, TooManyRedirects, RequestException
# import socket
from ssl import SSLError
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

app=Flask(__name__)


def handle_rest_response(response):
    parseJsonResponse = True
    if parseJsonResponse:
        last_json_response = json.loads(response) if len(response) > 1 else None
        return last_json_response
    else:
        return response



@app.route('/')
def hello_world():
    return "Hello World~~~"


@app.route('/cap')
def cap():
    api = 'https://api.coinmarketcap.com/v1/ticker/'

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
    table = '<table boder=1><tr><td>币</td><td>交易量$</td></tr>'
    for data in result:
        table = table + '<tr><td>' + data['symbol'] + '</td><td>' + data['24h_volume_usd'] + '</td></tr>'

    table = table + '</table>'
    return table
if __name__ == '__main__':
    app.run('0.0.0.0', 8899)

