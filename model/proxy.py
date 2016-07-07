#!/usr/bin/env python3
# coding:utf-8
import json
import re
import requests
import threading
import codecs
from queue import Queue

import time
from lxml import etree
from os import path
from selenium import webdriver
from bs4 import BeautifulSoup
try:
    from model.peuland import PeulandProxy
except ImportError:
    from peuland import PeulandProxy

js_path = path.join(path.dirname(path.abspath(__file__)), '../lib/phantomjs_2.1.1/bin/phantomjs')

def get_time_str():
    return time.strftime('%Y-%m-%d %H:%M:%S')

def get_soup(url):
    try:
        driver = webdriver.PhantomJS(js_path)
        driver.set_window_size(1366, 768)
        driver.get(url)
        driver.implicitly_wait(10)
        bodyStr= driver.find_element_by_tag_name("body").get_attribute("innerHTML")
        driver.quit()
        if bodyStr:
            soup = BeautifulSoup(bodyStr, "lxml")
            return soup
        else:
            return None
    except Exception as ex:
        print(ex)
        time.sleep(10)

class ProxyIp:
    @classmethod
    def get_proxy_ip_link(cls):
        url1 = "http://www.youdaili.net/"
        href_queue = Queue()  
        ip_queue = Queue()
        ip_valid = []
        soup = None
        box = None
        articles = []
        while not articles :
            soup = get_soup(url1)
            print(url1,get_time_str())
            articles = soup.select("div.m_box2 > ul > li > a")
            time.sleep(1)
        if articles:
            for i in articles:
                h = i.get("href")
                h_tail = h[-20:]
                if "guowai" in h_tail or "http" in h_tail or "QQ" in h_tail or "guonei" in h_tail or "Socks" in h_tail:
                    href_queue.put(h)
                    page_exits = None
                    while not page_exits:
                        soup = get_soup(h)
                        print(h,get_time_str())
                        page_exits = soup.select("ul.pagelist")
                        page_tag = soup.select("ul.pagelist > li > a")
                    if page_tag:
                        page = re.search(r"\d", page_tag[0].get_text()).group()
                        page = int(page)
                    else:
                        page = 1

                    for i in range(2,page+1):
                        href_queue.put(h[:-5]+"_"+str(i)+".html")
            return href_queue

    @classmethod
    def deduplication(cls):
        proxy_path = path.join(path.dirname(path.abspath(__file__)), '../static/proxy.txt')
        fe = codecs.open(proxy_path, "r+", "utf-8")
        ip = fe.readlines()
        ip = list(set(ip))
        print(len(ip),get_time_str())
        fe.close()
        with open(proxy_path,"w") as fe:
            for i in ip:
                fe.write(i)

    @classmethod
    def get_des_ip(cls, href_queue):
        ip_all = []
        ip_re = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{2,5}@[a-zA-Z0-9]{4,7})')
        while not href_queue.empty():
            ip_href = href_queue.get()
            ips = []
            while not ips:
                soup = get_soup(ip_href)
                ips = ip_re.findall(soup.text)
                #print(ips)
            ip_all += ips
        proxy_path = path.join(path.dirname(path.abspath(__file__)), '../static/proxy.txt')
        fe = codecs.open(proxy_path, "a", "utf-8")
        for i in ip_all:
            fe.write(i+"\n")
        fe.close()

    @classmethod
    def check_ip(cls):
        checkth = []
        ip_queue = Queue()
        proxy_path = path.join(path.dirname(path.abspath(__file__)), '../static/proxy.txt')
        fe = codecs.open(proxy_path, "r", "utf-8")
        ip_test = []
        for i in fe.readlines():
            if i not in ip_test:
                ip_test.append(i)
                ip_queue.put(i.strip())

        fe.close()
        ip_valid = []
        # print("Starting Checking...")
        for i in range(20):
            checkth.append(CheckThreads(ip_queue, ip_valid))
        for th in checkth:
            th.start()
        for th in checkth:
            th.join()
        proxy_pool_path = path.join(path.dirname(path.abspath(__file__)), '../static/proxy_pool.txt')
        f = codecs.open(proxy_pool_path, "w", "utf-8")
        # f = open(proxy_path, "w")
        for i in ip_valid:
            try:
                f.write(json.dumps(i) + "\n")
            except Exception as e:
                print(e)
        f.close()


class CheckThreads(threading.Thread):
    mutex = threading.Lock()

    def __init__(self, ip_queue, ip_valid, anonymous=False):
        super(CheckThreads, self).__init__()
        self.ip_queue = ip_queue
        self.ip_valid = ip_valid
        self.anonymous = anonymous

    def run(self):
        while not self.ip_queue.empty():

            ip_re = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{2,5})@([a-zA-Z0-9]{4,7})')
            ip = self.ip_queue.get()
            ip_se = ip_re.search(ip)
            if ip_se:
                ip_proxy = ip_se.group(1)
                ip_type = ip_se.group(2)
                #ip_site = re.search((u'([\u4e00-\u9fa5]+)'), ip).group()
                proxy = {ip_type: ip_proxy}
                #resp = requests.get(url="http://bj.ganji.com/", proxies=proxies, timeout=8)

                # try:
                #     r = requests.get('http://httpbin.org/ip', proxies=proxy, timeout=10)
                #     data = r.json()
                #     # é«å¿æ£æµ
                #     if self.anonymous:
                #         if data['origin'] == list(proxy.values())[0].split(':')[0]:
                #             self.ip_valid.append(proxy)
                #     if proxy not in self.ip_valid:
                #         self.ip_valid.append(proxy)
                #     time.sleep(1)
                # except Exception as e:
                #     print(e)

                try:
                    resp = requests.get("http://bj.ganji.com/",proxies=proxy)
                    if resp.status_code == 200:
                        self.ip_valid.append(proxy)
                    time.sleep(1)
                except Exception as ex:
                    print(ex)


if __name__ == "__main__":
    href_queue = ProxyIp.get_proxy_ip_link()
    ProxyIp.get_des_ip(href_queue)

    ProxyIp.deduplication()
    ProxyIp.check_ip()
    ins = PeulandProxy(20)
    ins.get_proxy()
    print("ok",get_time_str())
