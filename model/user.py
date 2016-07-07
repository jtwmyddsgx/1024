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
    for i in range(random_length-8):
        str_random += chars[random.randint(0, length)]
    str_random += time_str
    return str_random


class USER_LEVEL:
    BAN = 0
    NORMAL = 10
    ADMIN = 100


class User(BaseModel):
    username = TextField(index=True)
    password = TextField()
    salt = TextField()

    key = TextField(index=True)
    level = IntegerField()
    visit = IntegerField()

    reg_time = FloatField()
    key_time = FloatField()

    class Meta:
        db_table = 'users'

    def is_admin(self):
        return self.level == USER_LEVEL.ADMIN

    def refresh_key(self):
        self.key = random_str(32)
        self.key_time = int(time.time())
        self.save()

    @classmethod
    def new(cls, username, password):
        salt = random_str()
        password_md5 = md5(password.encode('utf-8')).hexdigest()
        password_final = md5((password_md5 + salt).encode('utf-8')).hexdigest()
        level = USER_LEVEL.ADMIN if cls.count() == 0 else USER_LEVEL.NORMAL  # 首个用户赋予admin权限
        the_time = time.time()
        return cls.create(username=username, password=password_final, salt=salt, level=level, key=random_str(32),
                          key_time=the_time, reg_time=the_time, visit=0)

    @classmethod
    def auth(cls, username, password):
        try:
            u = cls.get(cls.username == username)
        except DoesNotExist:
            return False
        password_md5 = md5(password.encode('utf-8')).hexdigest()
        password_final = md5((password_md5 + u.salt).encode('utf-8')).hexdigest()
        if u.password == password_final:
            return u

    @classmethod
    def exist(cls, username):
        return cls.select().where(cls.username == username).exists()

    @classmethod
    def update_pass(cls, username, password):
        try:
            user = cls.get(cls.username == username)
            salt = user.salt
            password_md5 = md5(password.encode('utf-8')).hexdigest()
            password_final = md5((password_md5 + salt).encode('utf-8')).hexdigest()
            User.update(password=password_final).where(User.username == username).execute()
        except DoesNotExist:
            return None

    @classmethod
    def set_level(cls, key, level):
        User.update(level=level).where(cls.key == key).execute()


    @classmethod
    def get_by_key(cls, key):
        try:
            return cls.get(cls.key == key)
        except DoesNotExist:
            return None

    @classmethod
    def get_by_name(cls, username):
        try:
            return cls.get(cls.username == username)
        except DoesNotExist:
            return None

    @classmethod
    def count(cls):
        return cls.select(cls.level > 0).count()

    @classmethod
    def get_all(cls):
        try:
            return cls.select().order_by(cls.id.asc())
        except DoesNotExist:
            return None

    @classmethod
    def visit_up(cls, username):
        try:
            user = cls.get(cls.username == username)
            visit_count = user.visit
            visit_count += 1
            User.update(visit=visit_count).where(User.username == username).execute()
        except DoesNotExist:
            return None

    @classmethod
    def num_lim(cls):
        if cls.count() >= 5000:
            return True
