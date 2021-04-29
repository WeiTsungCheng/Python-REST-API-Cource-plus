# Python-REST-API-Cource-

Udemy 課程 https://www.udemy.com/course/rest-api-flask-and-python


1. Section 6 ok
2. Section 8 使用 heroku postgres sql 出現 heroku 出現 H13錯誤 503.

解決方法 uwsgi -> gunicorn 
requirements 添加 SQLAlchemy, gunicorn 

但會出現 Internal Server Error 500
原因出在 SQLAlchemy==1.4.7 , SQLAlchemy 1.4.x has removed support for the postgres://

解法
import os
import re

uri = os.getenv("DATABASE_URL")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

參考
https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres


