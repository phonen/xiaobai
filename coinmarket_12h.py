# -*- coding: utf-8 -*-

import os
import sys
import pymysql

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

db = pymysql.connect("localhost","root","KeYpZrZx","btc")
cursor = db.cursor()
cursor.execute("truncate table coinmarket_12h")
db.commit()

sql1 = """select symbol,price_usd,volume from coinmarket where update_time<=UNIX_TIMESTAMP()-12*3600 and update_time> UNIX_TIMESTAMP() -12*3600-600"""
cursor.execute(sql1)
result1 = cursor.fetchall()
coin = {}
coind = {}
for row in result1:
    symbol = row[0]
    coind['price'] = row[1]
    coind['volume'] = row[2]

    coin[symbol] = coind


sql = """select symbol,price_usd,volume from coinmarket_last"""
cursor.execute(sql)

result = cursor.fetchall()

for row in result:

    symbol = row[0]
    if symbol in coin:
        price = row[1] - coin[symbol]['price']
        volume = row[2] - coin[symbol]['volume']
        try:
            sql = """insert into coinmarket_12h(symbol,price,volume) values ('%s',%s,%s)""" % (
                symbol, price, volume)
            print(sql)
            cursor.execute(sql)
            db.commit()
        except:
            print('error')
            db.rollback()







db.close()



