# coding:utf-8
import re

import math

from model import pagination
from model.comment import Comment
from model.user import User
from view import route, View, LoginView, AdminView, url_for, page_title
from model.article import Article


@route("/spider/([a-zA-Z0-9]{16,21})", name="article")
class Spider(View):
    def get(self, *args):
        key = args[0]
        ar = Article.get_by_key(key)
        page_size = 5
        comment_query = Comment.get_by_article(key)
        cur_page = self.get_argument("cur_page", int(math.ceil(comment_query.count() / page_size)))
        comment = pagination(count_all=comment_query.count(), query=comment_query, page_size=page_size, cur_page=cur_page)
        next_back = Article.get_next_back(key)
        if ar is not None:
            page_title = ar.header
            self.render(
                "spider.html",
                page_title=page_title,
                ar=ar,
                comment=comment,
                next_back=next_back,
            )
        else:
            self.messages.error("文章链接已经更新")
            self.redirect(url_for("index"))

    post = get


@route("/publish", name="publish")
class Publish(LoginView):
    def get(self):
        self.render(
            "publish.html",
            page_title="文章发布",
        )

    def post(self):
        header = self.get_argument("header", "")
        code = self.get_argument("code", "")
        describe = self.get_argument("describe", "")
        username = self.current_user().username
        error = False
        if self.is_admin():
            checked = 1
        else:
            checked = -1
        if header == "":
            self.messages.error("标题不能为空！")
            error = True
        if Article.num_lim(username):
            self.messages.error("文章过多，请联系管理员！")
            return self.redirect("/publish")
        elif not error and checked == 1:
            Article.new(username=username, header=header, code=code, describe=describe, checked=checked)
            self.messages.success("发表成功！")
        elif not error:
            Article.new(username=username, header=header, code=code, describe=describe, checked=checked)
            self.messages.success("等待管理员审核！")
        else:
            self.messages.warning("发表失败！")
        self.redirect("/")


@route("/comment", name="comment")
class CommentHandle(View):
    def post(self, *args, **kwargs):
        comment = self.get_argument("comment", "")
        user_re = re.compile(r"@(\S{3,19}) (.*)")
        try:
            foruser = user_re.search(comment).group(1)
            if not User.exist(foruser):
                foruser = ""
            else:
                comment = user_re.search(comment).group(2)
        except Exception as e:
            foruser = ""
        article_key = self.get_argument("article_key", "")
        user = self.current_user()
        if user is not None:
            username = user.username
        else:
            username = "游客"
        if user is not None and user.level == 0:
            self.messages.error("您暂时无法评论！")
        elif Comment.num_lim(username):
            self.messages.error("评论过多，暂时无法评论，请联系管理员！")
        elif comment != "":
            Comment.new(username, foruser, comment, article_key)
            self.messages.success("评论成功！")
        self.redirect("/spider/" + article_key)


@route("/comment/del", name="comment_del")
class CommentDel(View):
    def post(self, *args, **kwargs):
        comment_key = self.get_argument("theKey", "")
        user = self.current_user()
        comment = Comment.get_by_key(comment_key)
        if comment_key != "" and (user.level == 100 or user.username == comment.username):
            Comment.dele_by_key(comment_key)
            return self.write("删除成功")
        else:
            self.send_error(404)
