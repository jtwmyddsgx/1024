# coding:utf-8
import re

import math

from model import pagination
from view import route, url_for, View, LoginView, UnLoginView
from model.board import Board
from model.user import User
from lib.jsdict import JsDict
import time


# 留言板的页面
@route('/board', name='board')
class BoardView(View):
    def get(self):
        words_query = Board.get_all()  # 获得所有留言
        page_size = 5
        cur_page = self.get_argument("cur_page", int(math.ceil(words_query.count() / page_size)))
        words = pagination(count_all=words_query.count(), query=words_query, page_size=page_size, cur_page=cur_page)
        page_title = "联系站长"
        self.render(
            'board.html',
            words=words,
            page_title=page_title,
        )

    def post(self):
        words = self.get_argument('words', '')  # 用户的留言
        dele_by_key = self.get_argument('theKey', '')
        IP = self.request.headers["X-Forwarded-For"]
        user = self.current_user()
        username = None
        word_user = None
        word_username = None
        if user is None:
            user = JsDict()
            user.username = "游客"

        if dele_by_key != "":
            word_user = Board.get_one(Board.key == dele_by_key)
        if word_user is not None:
            word_username = word_user.username
        if user is not None:
            username = user.username
        if dele_by_key:
            if user.is_admin() or username == word_username:  # 如果不是admin用户将无法删除
                Board.dele_by_key(dele_by_key)
                self.write("删除成功！")
            else:
                self.write("您没有删除权限！")
        elif words:
            username = user.username
            user_re = re.compile(r"@(\S{3,19}) (.*)")
            try:
                foruser = user_re.search(words).group(1)
                if not User.exist(foruser):
                    foruser = ""
                else:
                    words = user_re.search(words).group(2)
            except Exception as e:
                foruser = ""
            if Board.num_lim(username):
                self.messages.error("留言过多，请联系管理员！")
                self.redirect("/board")
            elif user.username != "游客" and user.level == 0:
                self.messages.error("您暂时无法留言！")
                self.redirect(url_for("board"))
            else:
                Board.new(username, foruser, words, IP)
                self.messages.success("留言成功！")
                self.redirect(url_for("board"))
        else:
            self.redirect(url_for("board"))

        '''
        elif find_words:  # 模糊查询
            find_words_query = Board.get_by_words(find_words)
            self.messages.success("查询成功！")
        '''
