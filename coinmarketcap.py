# -*- coding: utf-8 -*-

import os
import sys
import requests

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')




api = 'https://api.coinmarketcap.com/v1/ticker/'


response = requests.get(api)
print(response)

