# coding:utf-8
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import time
import math
from tornado.concurrent import run_on_executor
from model import pagination
from model.article import Article
from model.authcode import VerifycationCode
from model.comment import Comment
from model.weather import GetWeather
from view import route, url_for, View, LoginView, UnLoginView, UnLoginView, tornado, AdminView
from model.user import User
from config import SIGNUP_KEY


@route('/signin', name='signin')
class SignIn(UnLoginView):
    def get(self):
        self.render(
            'user/signin.html'
        )

    def post(self):
        username = self.get_argument('username', "")
        password = self.get_argument('pwd', "")
        remember = self.get_argument('remember', False)
        next = self.get_argument('next', None)
        error = False

        u = User.auth(username, password)
        if not u:
            error = True
            self.messages.error("账号或密码错误！")
            if next:
                return self.redirect(next)
            return self.redirect(url_for("index"))

        if not error:
            self.messages.success('登录成功！')
            expires = 30 if remember else None
            self.set_secure_cookie('u', u.key, expires_days=expires)
            if next:
                return self.redirect(next)
            return self.redirect(url_for("index"))
        else:
            if next:
                return self.redirect(next)
            return self.redirect(url_for("index"))


@route('/signout', name='signout')
class SignOut(LoginView):
    def get(self, *args, **kwargs):
        next = self.get_argument("next", "")
        self.clear_cookie('u')
        self.messages.success("您已成功登出！")
        if next:
            return self.redirect(next)
        return self.redirect(url_for("index"))


@route('/signup', name='signup')
class SignUp(UnLoginView):
    def get(self):
        self.render(
            'user/signup.html'
        )

    def post(self):
        username = self.get_argument('username', '')
        password = self.get_argument('pwd1', '')
        password2 = self.get_argument('pwd2', '')
        verify_code = self.get_argument('verify_code', '').lower()
        next = self.get_argument('next', None)
        error = SIGNUP_KEY
        if len(username) < 3 or len(username) > 18:
            error = True
            self.messages.error('用户长度必须大于3小于18！')
        if password != password2:
            error = True
            self.messages.error('您输入的密码不一致！！')
        if len(password) < 3 or len(password) > 51:
            error = True
            self.messages.error('密码长度必须大于3小于50！')
        if User.exist(username):
            error = True
            self.messages.error('用户已存在！')
        if User.num_lim():
            error = True
            self.messages.error("注册用户过多，请联系管理员")
        '''
        if self.session['verify_code'] != verify_code:
            error = True
            self.messages.error('验证码不正确！')
            self.session['verify_code'] = ''
        '''
        if not error:
            User.new(username, password)
            u = User.auth(username, password)
            self.set_secure_cookie('u', u.key)
            self.messages.success('账户创建成功！')
            if next:
                return self.redirect(next)
            self.redirect('/')
        else:
            if next:
                return self.redirect(next)
            self.redirect('/')


@route('/verifycode', name='verifycode')
class VerifyCode(UnLoginView):
    def get(self):
        vc = VerifycationCode()
        code_img = vc.create_validate_code()
        image_code = code_img[1]
        # image_path = path.join(path.dirname(path.abspath(__file__)), '..\\static\\verify_img\\validate.gif')
        # code_img[0].save(image_path, "GIF")
        buffer = BytesIO()
        code_img[0].save(buffer, 'gif', quality=100)
        code_img[0].close()
        self.set_header('Content-Type', 'image/jepg')
        self.session['verify_code'] = image_code.lower()  # 校验码不区分大小写
        self.write(buffer.getvalue())


@route('/alertpass', name='alertpass')
class AlertPass(LoginView):
    def get(self):
        self.render('user/alertpass.html')

    def post(self):
        password1 = self.get_argument('password1', '')
        password2 = self.get_argument('password2', '')
        username = self.current_user().username
        next = self.get_argument("next", "")
        error = False
        if len(password1) < 3 or len(password1) > 18:
            error = True
            self.messages.error('密码长度必须大于3小于18！')
        if len(password2) < 3 or len(password2) > 18:
            error = True
            self.messages.error('密码长度必须大于3小于18！')
        if password1 != password2:
            error = True
            self.messages.error('您输入的密码不一致！')
        if not User.exist(username):
            error = True
            self.messages.error('用户不存在！')
        if not error:
            User.update_pass(username, password1)
            self.messages.success('账户密码修改成功！')
            if next:
                return self.redirect(next)
            self.redirect('/')
        else:
            if next:
                return self.redirect(next)
            self.redirect('/')


@route('/user/manager/([0-9]{0,8})/([a-zA-Z0-9]{0,32})', name="user_manager")
class UserManager(AdminView):
    def get(self, *args, **kwargs):
        set_type = args[0]
        key = args[1]
        if key is not None:
            if set_type == "0":
                User.set_level(key, 0)
                self.messages.success("该用户已进黑名单！")
            elif set_type == "1":
                User.set_level(key, 10)
                self.messages.success("该用户回复正常！")
            elif set_type == "2":
                User.set_level(key, 100)
                self.messages.success("该用户已提升为管理员！")
            return self.redirect("/manager/admin/2")
        else:
            self.messages.error("请检查操作是否正确！")
            return self.redirect("/manager/admin/2")


@route("/manager/admin/([a-zA-Z0-9]{0,21})", name="admin_manager")
class AdminManager(AdminView):
    def get(self, *args):
        key = args[0]
        if key == "1":
            article_query = Article.get_all()
            page_size = 5
            #cur_page = self.get_argument("cur_page", int(math.ceil(article_query.count() / page_size)))
            cur_page = self.get_argument("cur_page", 1)
            article = pagination(count_all=article_query.count(), query=article_query, page_size=page_size,
                                 cur_page=cur_page)
            self.render(
                'user/manager.html',
                article=article,
                users={},
                page_title="文章管理",
            )
        elif key == "2":
            user_query = User.get_all()
            page_size = 5
            cur_page = self.get_argument("cur_page", int(math.ceil(user_query.count() / page_size)))
            users = pagination(count_all=user_query.count(), query=user_query, page_size=page_size, cur_page=cur_page)
            self.render(
                'user/manager.html',
                article={},
                users=users,
                page_title="用户管理",
            )
        else:
            self.redirect("/manager/" + key)


@route("/checked/([a-zA-Z0-9]{16,20})", name="article_check")
class SpiderChecked(AdminView):
    def get(self, *args, **kwargs):
        key = args[0]
        article = Article.get_by_key(key)
        if article.checked == -1:
            Article.check_pass(key)
            self.messages.success("审核通过！")
        elif article.checked == 1:
            Article.check_fail(key)
            self.messages.error("禁止成功！！")
        self.redirect("/manager/admin/1")


@route("/exist", name="exist_user")
class UserExistCheck(View):
    def get(self, *args, **kwargs):
        username = self.get_argument("username", "")
        if len(username) < 3:
            return self.write("用户名长度必须大于2！")
        elif len(username) > 18:
            return self.write("用户名长度必须小于18")
        if username != "":
            existed = User.exist(username)
            if existed:
                self.write("该用户已存在..")
            else:
                self.write("该用户可用.")
        else:
            self.send_error(status_code=404)


@route("/user/personal/manager/([0-9]{0,3})", name="personal_manager")
class PersonalManager(LoginView):
    def get(self, *args, **kwargs):
        user = self.current_user()
        stype = args[0]
        if stype == "1":
            article_query = Article.get_by_username(user.username)
            page_size = 5
            cur_page = self.get_argument("cur_page", int(math.ceil(article_query.count() / page_size)))
            article = pagination(count_all=article_query.count(), query=article_query, page_size=page_size,
                                 cur_page=cur_page)
            self.render(
                'personal/manager.html',
                article=article,
                comment={},
                forperson={},
                page_title="文章管理",
            )
        elif stype == "2":
            comment_query = Comment.get_by_username(user.username)
            forperson_query = Comment.get_by_foruser(user.username)
            page_size = 5
            cur_page1 = self.get_argument("cur_page1", int(math.ceil(comment_query.count() / page_size)))
            cur_page2 = self.get_argument("cur_page2", int(math.ceil(forperson_query.count() / page_size)))
            comment = pagination(count_all=comment_query.count(), query=comment_query, page_size=page_size,
                                 cur_page=cur_page1)
            forperson = pagination(count_all=forperson_query.count(), query=forperson_query, page_size=page_size,
                                   cur_page=cur_page2)
            self.render(
                'personal/manager.html',
                article={},
                comment=comment,
                forperson=forperson,
                page_title="评论管理",
            )
        else:
            return self.redirect(url_for("index"))

    def post(self, *args, **kwargs):
        stype = args[0]
        if stype == "1":
            article_key = self.get_argument("theKey", "")
            user = self.current_user()
            article = Article.get_by_key(article_key)
            if article_key != "" and(user.level == 100 or user.username == article.username):
                if Article.dele_by_key(article_key):
                    Comment.dele_by_article(article_key)
                    self.write("删除成功！")
                else:
                    self.send_error(404)
            else:
                self.send_error(404)
        if stype == "2":
            comment_key = self.get_argument("theKey", "")
            user = self.current_user()
            comment = Comment.get_by_key(comment_key)
            if comment_key != "" and (user.level == 100 or user.username == comment.username):
                if Comment.dele_by_key(comment_key):
                    self.write("删除成功！")
                else:
                    self.send_error(404)
            else:
                self.send_error(404)
        else:
            self.redirect("/user/personal/manager/1")


@route("/manager/article", name="article_manager")
class ArticleManager(LoginView):
    def post(self, *args, **kwargs):
        key = self.get_argument("theKey", "")
        user = self.current_user()
        article = Article.get_by_key(key)
        if key != "" and(user.level == 100 or user.username == article.username):
            if Article.dele_by_key(key):
                Comment.dele_by_article(key)
                self.write("删除成功！")
            else:
                self.send_error(404)
        else:
            self.send_error(404)
