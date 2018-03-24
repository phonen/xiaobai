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

sql2 = """select symbol,price_usd,volume from coinmarket where update_time<=UNIX_TIMESTAMP()-48*3600 and update_time> UNIX_TIMESTAMP() -48*3600-600"""
cursor.execute(sql2)
result2 = cursor.fetchall()
coin2 = {}
coind2 = {}
for row in result2:
    symbol = row[0]
    coind2['price'] = row[1]
    coind2['volume'] = row[2]

    coin2[symbol] = coind2


sql = """select symbol,price_usd,volume from coinmarket_last"""
cursor.execute(sql)

result = cursor.fetchall()

for row in result:

    symbol = row[0]
    if symbol in coin and symbol in coin2:
        price = row[1] - coin[symbol]['price']
        volume = row[2] - coin[symbol]['volume']
        volume48 = row[2] - coin2[symbol]['volume']
        price48 = row[2] - coin2[symbol]['price']
        try:
            sql = """insert into coinmarket_12h(symbol,price,volume,price48,volume48) values ('%s',%s,%s,%s,%s)""" % (
                symbol, price, volume,price48,volume48)
            print(sql)
            cursor.execute(sql)
            db.commit()
        except:
            print('error')
            db.rollback()







db.close()



