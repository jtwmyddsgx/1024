# coding:utf-8
import time
from concurrent.futures import ThreadPoolExecutor
import tornado
import os
import codecs
from tornado.concurrent import run_on_executor
from model.proxy import ProxyIp
from view import route, LoginView, View, AdminView

'''
@route("/proxy_pool",name="proxy_pool")
class ProxyJson(View):
    def get(self,*args,**kwargs):
        proxy_pool_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static/proxy_pool.txt')
        proxy_ips = []
        with open(proxy_pool_path,"r") as pool:
            for i in pool.readlines():
                proxy_ips.append(i.strip())
        
        self.write(proxy_ips)
'''
@route("/proxy", name="proxy")
class Proxy(AdminView):
    executor = ThreadPoolExecutor(2)

    def get(self, *args, **kwargs):
        proxy_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static/proxy.txt')
        f = codecs.open(proxy_path, "r", "utf-8")
        #f = open(proxy_path, "r")
        statinfo = os.stat(proxy_path)
        update_time = statinfo.st_mtime
        update_time = time.localtime(update_time)
        update_time = "%s/%s/%s %s:%s:%s" % (
            update_time.tm_year, update_time.tm_mon, update_time.tm_mday, update_time.tm_hour, update_time.tm_min,
            update_time.tm_sec)
        ips = []
        for i in f.readlines():
            ips.append(i.strip())
        ips_len = len(ips)
        self.render(
            "proxy.html",
            update_time=update_time,
            ips=ips,
            ips_len=ips_len,
            page_title="代理ip"
        )

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        #yield self.get_proxy()
        self.finish("更新完毕！")

    @run_on_executor
    def get_proxy(self):
        ProxyIp.get_proxy_ip()
