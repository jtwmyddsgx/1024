# coding:utf-8
from random import Random
import time
from peewee import RawQuery
from model import BaseModel
from peewee import *


def random_str(random_length=16):
    str_random = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    time_str = str(hex(int(time.time())))[-8:]
    for i in range(random_length-8):
        str_random += chars[random.randint(0, length)]
    str_random += time_str
    return str_random


class Article(BaseModel):
    username = TextField(index=True)
    publish_time = TextField(index=True)
    header = TextField(index=True)
    type = TextField(index=True)
    code = TextField()
    describe = TextField()
    key = TextField(index=True)
    key_time = FloatField()
    checked = IntegerField(index=True)

    class Meta:
        db_table = "article"

    @classmethod
    def new(cls, username, header, code, describe, checked):
        publish_time = time.asctime(time.localtime(time.time()))
        key = str(hex(int(time.time() / 86400)))[2:] + random_str(16)
        key_time = time.time()
        return cls.create(username=username, publish_time=publish_time, header=header, type="default",
                          code=code, describe=describe, key=key, key_time=key_time, checked=checked)

    @classmethod
    def get_all(cls):
        article_query = cls.select().order_by(cls.id.desc())
        return article_query

    @classmethod
    def get_next_back(cls, key):
        article_all = cls.get_all()
        article_back_key = -1
        article_next_key = -1
        for i in article_all:
            if i.key != key and i.checked == 1:
                article_back_key = i.key
            elif i.key == key:
                break
        for i in article_all[::-1]:
            if i.key != key and i.checked == 1:
                article_next_key = i.key
            elif i.key == key:
                break
        return [article_back_key, article_next_key]

    @classmethod
    def dele_by_id(cls, article_id):
        cls.get_one(cls.id == article_id).delete_instance()

    @classmethod
    def get_by_key(cls, key):
        return cls.get_one(cls.key == key)


    @classmethod
    def get_by_id(cls, id):
        try:
            return cls.get(cls.id == id)
        except DoesNotExist:
            return None

    @classmethod
    def dele_by_key(cls, key):
        x = cls.get_by_key(key)
        return x.delete_instance() if x is not None else False

    @classmethod
    def get_by_username(cls, username):
        try:
            return cls.select().where(cls.username == username)
        except DoesNotExist:
            return None

    @classmethod
    def dete_by_key(cls,key):
        x = cls.get_by_key(key)
        x.delete_instance() if x is not None else None

    @classmethod
    def get_by_words(cls, words):
        words = "%" + words + "%"
        rq = RawQuery(cls, "select * from words where words like ?", words)
        return rq.execute()

    @classmethod
    def check_pass(cls, key):
        cls.update(checked=1).where(cls.key == key).execute()

    @classmethod
    def check_fail(cls, key):
        cls.update(checked=-1).where(cls.key == key).execute()

    @classmethod
    def count(cls, username):
        return cls.select().where(cls.username == username).count()

    @classmethod
    def num_lim(cls, username):
        if cls.count(username) >= 100:
            return True

    @classmethod
    def count_all(cls):
        return cls.select().count()

    @classmethod
    def get_one(cls, *query, **kwargs):
        try:
            return cls.get(*query, **kwargs)
        except DoesNotExist:
            return None
