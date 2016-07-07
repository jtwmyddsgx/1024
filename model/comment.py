# coding:utf-8

import time
from peewee import *
from hashlib import md5
from random import Random
from model import BaseModel


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


class USER_LEVEL:
    BAN = 0
    NORMAL = 10
    ADMIN = 100


class Comment(BaseModel):
    username = TextField(index=True)
    foruser = TextField(index=True)
    comment = TextField(index=True)
    article_key = TextField(index=True)
    key = TextField(index=True)
    comment_time = TextField(index=True)
    key_time = FloatField()

    class Meta:
        db_table = 'comments'

    def is_admin(self):
        return self.level == USER_LEVEL.ADMIN

    def refresh_key(self):
        self.key = random_str(32)
        self.key_time = int(time.time())
        self.save()

    @classmethod
    def new(cls, username, foruser, comment, article_key):
        key = random_str()
        key_time = time.time()
        comment_time = time.asctime(time.localtime(time.time()))
        return cls.create(username=username, foruser=foruser, comment=comment, article_key=article_key, key=key,
                          comment_time=comment_time, key_time=key_time)

    @classmethod
    def get_by_key(cls, key):
        try:
            return cls.get(cls.key == key)
        except DoesNotExist:
            return None

    @classmethod
    def dele_by_article(cls, key):
        article_comment = cls.select().where(cls.article_key == key)
        for i in article_comment:
            if i is not None:
                i.delete_instance()

    @classmethod
    def dele_by_id(cls, comment_id):
        x = cls.get_one(cls.id == comment_id)
        if x is not None:
            x.delete_instance()

    @classmethod
    def dele_by_key(cls, comment_key):
        x = cls.get_one(cls.key == comment_key)
        return x.delete_instance() if x is not None else False

    @classmethod
    def count(cls, username):
        return cls.select().where(cls.username == username).count()

    @classmethod
    def num_lim(cls, username):
        if cls.count(username) >= 100:
            return True

    @classmethod
    def get_all(cls):
        try:
            return cls.select().order_by(cls.id.asc())
        except DoesNotExist:
            return None

    @classmethod
    def get_by_article(cls, article_key):
        return cls.select().where(cls.article_key == article_key).order_by(cls.id.asc())

    @classmethod
    def get_by_username(cls, username):
        return cls.select().where(cls.username == username).order_by(cls.id.asc())

    @classmethod
    def get_by_foruser(cls, username):
        return cls.select().where(cls.foruser == username).order_by(cls.id.asc())

    @classmethod
    def get_one(cls, *query, **kwargs):
        try:
            return cls.get(*query, **kwargs)
        except DoesNotExist:
            return None
