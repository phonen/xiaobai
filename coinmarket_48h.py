# -*- coding: utf-8 -*-

import os
import sys
import pymysql

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

db = pymysql.connect("localhost","root","KeYpZrZx","btc")
cursor = db.cursor()
cursor.execute("truncate table coinmarket_48h")
db.commit()


sql = """select a.symbol as symbol,a.price as price,a.volume as volume,b.price_usd as price12,b.volume as volume12,c.price_usd as price48,c.volume as volume48 from coinmarket_last a,(select symbol,price_usd,volume from coinmarket where update_time<=UNIX_TIMESTAMP()-12*3600 and update_time> UNIX_TIMESTAMP() -12*3600-600) b,(select symbol,price_usd,volume from coinmarket where update_time<=UNIX_TIMESTAMP()-48*3600 and update_time> UNIX_TIMESTAMP() -48*3600-600) c
where a.symbol=b.symbol and a.symbol=c.symbol"""
cursor.execute(sql)

result = cursor.fetchall()

for row in result:

    symbol = row[0]
    price = row[1]
    volume = row[2]
    price12 = row[3]
    volume12 = row[4]
    price48 = row[5]
    volume48 = row[6]
    try:
        sql = """insert into coinmarket_48h(symbol,price,volume，price12,volume12,price48,volume48) values ('%s',%s,%s,%s,%s,%s,%s)""" % (
            symbol, price, volume,price12,volume12,price48,volume48)
        print(sql)
        cursor.execute(sql)
        db.commit()
    except:
        print('error')
        db.rollback()







db.close()



