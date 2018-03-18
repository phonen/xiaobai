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
    sql1 = """SELECT price_usd,volume,last_updated from coinmarket where symbol='%s' ORDER BY last_updated desc limit 1""" % (symbol)
    cursor.execute(sql1)
    result1 = cursor.fetchone()
    price1 = result1[0]
    volume1 = result1[1]
    last1 = result1[2]
    sql2 = """select price_usd,volume,last_updated from coinmarket where symbol='%s' and last_update<=%s - 12*3600 order by last_updated desc limit 1""" % (symbol,last1)
    cursor.execute(sql2)
    result2 = cursor.fetchone()
    price2 = result2[0]
    volume2 = result2[1]
    last2 = result2[2]
    print(sql1)
    print(sql2)
    try:
        sql = """insert into coinmarket_12h(symbol,price,volume) values ('%s',%s,%s)""" % (
        symbol, price1 - price2, volume1 - volume2)
        print(sql)
        cursor.execute(sql)
        db.commit()
    except:
        print('error')
        db.rollback()

db.close()



