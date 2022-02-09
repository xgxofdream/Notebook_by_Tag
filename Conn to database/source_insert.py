# -*- coding: utf-8 -*-
"""
mySql database connection

Created on Sat Jan 29 22:13:06 2022

@Author: Jie Liu, liujie.dhu@gmail.com

"""

import pymysql

# 连接数据库
db = pymysql.connect(host='localhost', user='root', passwd='xgx8267789', db='myenglish', port=3306, charset='utf8')

# 生成游标对象
cursor = db.cursor()

# 书的页码
start_page = 1
end_page = 319
chap = ""

# 数据库操作
try:
    while start_page <= end_page:
        page = 'Page S-'+str(start_page)
        start_page = start_page + 1



        # sql语句
        sql = "INSERT INTO `myenglish`.`english_reference` (" \
              "`english_text_location`, `note`, `source_id`" \
              ") VALUES ('" + page +"', '" + chap +"', '15')"

        print (sql)
        cursor.execute(sql)
        db.commit()

except Exception as e:
    print("失败:", e)
    # 发生错误时，回滚
    db.rollback()

# 关闭游标
cursor.close()

# 关闭连接
db.close