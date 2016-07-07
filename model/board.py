# coding:utf-8
from peewee import RawQuery
from model import BaseModel
from peewee import *
from random import Random
import time


def random_str(random_length=16):
    str_random = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    time_str = str(hex(int(time.time())))[-8:]
    for i in range(random_length - 8):
        str_random += chars[random.randint(0, length)]
    str_random += time_str
    return str_random


class Board(BaseModel):
    username = TextField(index=True)
    foruser = TextField(index=True)
    words = TextField(index=True)
    make_time = TextField(index=True)
    key = TextField(index=True)
    key_time = TextField(index=True)
    IP = TextField(index=True)

    class Meta:
        db_table = "words"

    @classmethod
    def new(cls, username, foruser, words, IP):
        the_time = time.time()
        key = random_str()
        make_time = time.localtime(time.time())
        make_time = "%s年%s月%s日%s:%s" % (make_time.tm_year, make_time.tm_mon, make_time.tm_mday, make_time.tm_hour,make_time.tm_min)
        return cls.create(username=username, foruser=foruser, words=words, make_time=make_time, key=key,
                          key_time=the_time, IP=IP)

    @classmethod
    def get_all(cls):
        words_query = cls.select().order_by(cls.id.asc())
        return words_query

    @classmethod
    def dele_by_id(cls, word_id):
        de = cls.get_one(cls.id == word_id)
        if de is not None:
            de.delete_instance()
            return True
        else:
            return False

    @classmethod
    def dele_by_key(cls, word_key):
        x = cls.get_one(cls.key == word_key)
        x.delete_instance() if x is not None else None

    @classmethod
    def get_by_username(cls, username):
        return cls.get_one(cls.username == username)

    @classmethod
    def get_by_words(cls, words):
        words = "%" + words + "%"
        rq = RawQuery(cls, "select * from words where words like ?", words)
        return rq.execute()

    @classmethod
    def get_by_make_time(cls, make_time):
        return cls.get_one(cls.make_time == make_time)

    @classmethod
    def count(cls, username):
        return cls.select().where(cls.username == username).count()

    @classmethod
    def num_lim(cls, username):
        if cls.count(username) >= 100:
            return True

    @classmethod
    def get_one(cls, *query, **kwargs):
        try:
            return cls.get(*query, **kwargs)
        except DoesNotExist:
            return None
