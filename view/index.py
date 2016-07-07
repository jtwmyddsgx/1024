# coding:utf-8
from model import pagination
from view import route, url_for, View
from model.user import User
from model.article import Article


@route('/t', name='indexx')
class Index(View):
    def get(self):
        u = self.current_user()
        if u:
            username = self.current_user().username
            User.visit_up(username)
        self.render(
            'index.html'
        )


@route("/", name="index")
class Community(View):
    def get(self, *args, **kwargs):
        cur_page = self.get_argument("cur_page", "1")
        article_query = Article.get_all()
        article = pagination(count_all=article_query.count(), query=article_query, page_size=5, cur_page=cur_page)
        self.render(
            'community.html',
            article=article,
        )



