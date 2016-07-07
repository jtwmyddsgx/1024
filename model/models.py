# coding:utf-8

from model import db
from model.article import Article
from model.comment import Comment
from model.user import User
from model.board import Board

db.connect()
db.create_tables([User, Article, Board, Comment], safe=True)
