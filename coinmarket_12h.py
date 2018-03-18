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
sql = """select symbol from coinmarket_last"""
cursor.execute(sql)

result = cursor.fetchall()
for row in result:
    symbol = row[0]
    sql1 = """SELECT * from coinmarket where symbol='%s' ORDER BY last_updated desc limit 1""" % (symbol)
    cursor.execute(sql1)
    result1 = cursor.fetchone()
    price1 = result1['price_usd']
    volume1 = result1['24h_volume_usd']
    last1 = result1['last_updated']
    sql2 = """select * from coinmarket where symbol='%s' and last_update<=%s - 12*3600 order by last_updated desc limit 1""" % (symbol,last1)
    cursor.execute(sql2)
    result2 = cursor.fetchone()
    price2 = result2['price_usd']
    volume2 = result2['24h_volume_usd']
    last2 = result2['last_updated']
    try:
        sql = """insert into coinmarket_12h(symbol,price,volume) values ('%s',%s,%s)""" % (
        symbol, price1 - price2, volume1 - volume2)
        cursor.execute(sql)
        db.commit()
    except:
        print('error')
        db.rollback()

db.close()



