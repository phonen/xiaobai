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


sql = """select d.id as coinid,d.name as name,d.symbol as symbol,a.price_usd as price,a.volume as volume,b.price_usd as price12,b.volume as volume12,c.price_usd as price48,c.volume as volume48,e.price_usd as price24,e.volume as volume24 
from coins d,coinmarket_last a,
(select coinid,price_usd,volume from coinmarket where update_time<=UNIX_TIMESTAMP()-12*3600 and update_time> UNIX_TIMESTAMP() -12*3600-600) b,
(select coinid,price_usd,volume from coinmarket where update_time<=UNIX_TIMESTAMP()-48*3600 and update_time> UNIX_TIMESTAMP() -48*3600-600) c,
(select coinid,price_usd,volume from coinmarket where update_time<=UNIX_TIMESTAMP()-24*3600 and update_time> UNIX_TIMESTAMP() -24*3600-600) e
where d.id=a.coinid and d.id=b.coinid and d.id=c.coinid and d.id=e.coinid"""
cursor.execute(sql)

result = cursor.fetchall()

for row in result:
    id = row[0]
    name = row[1]
    symbol = row[2]
    price = row[3]
    volume = row[4]
    price12 = row[5]
    volume12 = row[6]
    price48 = row[7]
    volume48 = row[8]
    price24 = row[9]
    volume24 = row[10]
    try:
        sql = """insert into coinmarket_48h(id,symbol,price,volume,price12,volume12,price48,volume48,price24,volume24) values ('%s','%s',%s,%s,%s,%s,%s,%s,%s,%s)""" % (
            id,symbol, price, volume,price12,volume12,price48,volume48,price24,volume24)
        print(sql)
        cursor.execute(sql)
        db.commit()
    except:
        print('error')
        db.rollback()







db.close()



