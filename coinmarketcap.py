# -*- coding: utf-8 -*-

import os
import sys
from requests import Session

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')




api = 'https://api.coinmarketcap.com/v1/ticker/'

request = Session()
response = request.get(api)
print(response)

