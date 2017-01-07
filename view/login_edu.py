# coding=utf-8
import datetime
import re
import requests
import os
from lxml import etree
from os import path
from view import route, View, LoginView
import time


@route("/edu", name="edu")
class LoginEdu(View):
    hosturl = 'http://jwgl.fjnu.edu.cn/'  # 登陆时的主页
    posturl = 'http://jwgl.fjnu.edu.cn/default2.aspx'  # 通过查看HTML网页源代码找出登陆时POST所提交的网址

    resp = requests.session()  # 建立会话

    # 使用firebug查看元素，将请求头信息复制黏贴如下
    # cookie没有添加其中
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding': 'gzip,deflate',
               'Accept-Language': 'zh-CN,zh;q=0.8',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Host': 'jwgl.fjnu.edu.cn',
               'Referer': 'http://jwgl.fjnu.edu.cn/',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:39.0) Gecko/20100101'}

    # 将验证码图片写入指定文件夹，并使用默认程序打开
    image_path = path.join(path.dirname(path.abspath(__file__)), '../static/img/yzm.jpg')

    trs = []
    trs_t = []
    update_time = time.localtime().tm_mday

    def get(self, *args, **kwargs):
        if self.trs != [] and self.trs_t != [] and self.update_time == time.localtime().tm_mday:
            return self.render(
                "edu.html",
                trs=self.trs,
                trs_t=self.trs_t
            )
        if self.update_time != time.localtime().tm_mday:
            self.trs = []
            self.trs_t = []
        try:
            r = self.resp.get("http://jwgl.fjnu.edu.cn/xs_main.aspx?xh=119052013028")
            headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                       'Accept-Encoding': 'gzip,deflate',
                       'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                       'Connection': 'keep-alive',
                       'Host': 'jwgl.fjnu.edu.cn',
                       'Referer': 'http://jwgl.fjnu.edu.cn/xs_main.aspx?xh=' + "119052013028",
                       }
            page1 = etree.HTML(r.text)
            infourl = page1.xpath("//div[@id='headDiv']/ul/li[5]/ul/li[2]/a")[0].get('href')
            infourl = 'http://jwgl.fjnu.edu.cn/' + infourl
            week_day = datetime.datetime.now().weekday() + 1
            week_day_1 = (week_day % 7) + 1
            # 得到个人信息里的信息，找到行政班一格，抓出其文本信息，即我们所要找的信息
            res = self.resp.get(infourl, headers=headers)
            text = re.sub(r"<br>|&nbsp;", "", res.text)
            page2 = etree.HTML(text)
            trs = []
            trs_t = []
            for i in range(1, 15):
                try:
                    x = page2.xpath(
                        "//table[@id='Table1']/tr[" + str(i) + "]/td[@align='Center'][" + str(week_day) + "]/text()")[0]
                    trs.append(x)
                    self.trs.append(x)
                except IndexError as e:
                    trs.append("")
                    self.trs.append("")
                try:
                    x_1 = page2.xpath(
                        "//table[@id='Table1']/tr[" + str(i) + "]/td[@align='Center'][" + str(week_day_1) + "]/text()")[
                        0]
                    trs_t.append(x_1)
                    self.trs_t.append(x_1)
                except IndexError as e:
                    trs_t.append("")
                    self.trs_t.append("")
            time_day = time.localtime().tm_mday
            self.update_time = time_day
            return self.render(
                "edu.html",
                trs=trs,
                trs_t=trs_t,
                page_title="个人课表"
            )
        except IndexError:
            image_path = path.join(path.dirname(path.abspath(__file__)), '../static/img/yzm.jpg')
            fp = open(image_path, 'wb')
            image = self.resp.get("http://jwgl.fjnu.edu.cn/CheckCode.aspx", headers=self.headers)
            fp.write(image.content)
            fp.close()
            self.render(
                "edu.html",
                trs=None,
                trs_t=None,
            )

    def post(self, *args, **kwargs):
        yzm = self.get_argument("yzm", "")
        trs = None
        trs_t = None
        if yzm != "":
            try:
                r = self.resp.get(self.hosturl, headers=self.headers)
                page = etree.HTML(r.text)
                viewstate = page.xpath("//input[@name='__VIEWSTATE']")[0].get("value")

                # 登陆时所用的账号密码以及验证码
                login_data = {'__VIEWSTATE': viewstate, 'txtUserName': 'username',
                              'TextBox2': 'password', 'txtSecretCode': yzm,
                              'RadioButtonList1': '%D1%A7%C9%FA',
                              'Button1': '', 'hidPdrs': '', 'hidsc': '', 'lbLanguage': ''}

                # 将登陆信息POST到指定网址，完成登陆
                r = self.resp.post(self.posturl, login_data)
            except Exception as e:
                print(e)
                return self.redirect("/edu")
            finally:
                return self.redirect("/edu")


if __name__ == "__main__":
    l = LoginEdu()
    l.login()
