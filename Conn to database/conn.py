# -*- coding: utf-8 -*-
"""
mySql database connection

Created on Sat Jan 29 22:13:06 2022

@Author: Jie Liu, liujie.dhu@gmail.com

"""

import pymysql
# 连接数据库
db = pymysql.connect(host='localhost',user='root',passwd='xgx8267789',db='myenglish',port=3306,charset='utf8')

# 生成游标对象
cursor = db.cursor()

# 数据库操作
try:

    # sql语句
    sql_select = 'SELECT * FROM english_data WHERE id = 30'
    
    # 这个是执行sql语句，返回的是影响的条数
    data = cursor.execute(sql_select)
    
    # 得到一条数据
    one = cursor.fetchone()
    
    # 打印数据
    print(one)
    
except Exception as e:
    print("失败:", e)
else:
    db.commit()
    if():
        print("成功。")
    
# 关闭游标
cursor.close()
    
# 关闭连接
db.close