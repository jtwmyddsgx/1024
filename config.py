# coding:utf-8

PORT = 9000
DEBUG = False
TITLE = 'Web Crawler'
TEMPLATE = 'mako'  # jinja2/mako/tornado
DATABASE_URI = "sqlite:///database.db"
COOKIE_SECRET = "6aOO5ZC55LiN5pWj6ZW/5oGo77yM6Iqx5p+T5LiN6YCP5Lmh5oSB44CC"
SIGNUP_KEY = False
AUTHCODE_FONT = "static/fonts/arialbi.ttf"
try:
    from private import *
except:
    pass
