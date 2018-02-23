# -*- coding: utf-8 -*-

import os
import sys

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

import ccxt  # noqa: E402
import key

binance = ccxt.binance(key.binance)
print(binance.fetch_balance())
zb = ccxt.zb(key.zb)
print(zb.fetch_balance())