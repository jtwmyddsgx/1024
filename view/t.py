import re
import requests
import threading
from queue import Queue
from lxml import etree


class ProxyIp:
    @classmethod
    def get_proxy_ip(cls):
        url1 = "http://www.youdaili.net/"
        href_queue = Queue()  # 到该网站找到需要抓取ip的链接
        ip_queue = Queue()  # 网站上能找到的ip
        ip_valid = []  # 有效的代理

        url1_resp = requests.get(url1)
        content = url1_resp.content.decode()
        html = etree.HTML(content)
        box = html.xpath("//div[@class='m_box2']/ul/li/a")
        for i in range(24):
            href_queue.put(box[i].get("href"))  # 将链接放到队列里

        while not href_queue.empty():  # 获取所有代理
            ip_href = href_queue.get()
            try:
                resp = requests.get(ip_href)
                content = resp.content.decode()
                html = etree.HTML(content)
                ips = html.xpath("//div[@class='cont_font']/p/span[1]")
                for ip in ips[0].itertext():
                    ip_queue.put(ip)
            except Exception as e:
                print(e)
                break

        checkth = []
        print("Starting Checking...")
        for i in range(30):  # 使用多线程进行验证是否可用
            checkth.append(CheckThreads(ip_queue, ip_valid))
        for th in checkth:
            th.start()
        for th in checkth:
            th.join()
        ip_valid = list(set(ip_valid))
        return ip_valid


class CheckThreads(threading.Thread):
    mutex = threading.Lock()

    def __init__(self, ip_queue, ip_valid):
        super(CheckThreads, self).__init__()
        self.ip_queue = ip_queue
        self.ip_valid = ip_valid

    def run(self):
        while not self.ip_queue.empty():
            try:
                ip_re = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{2,5})')
                ip = self.ip_queue.get()
                ip_proxy = ip_re.search(ip).group()
                ip_site = re.search((u'([\u4e00-\u9fa5]+)'),ip).group()
                proxies = {"http": ip_proxy}
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Host": "www.1356789.com",
                    "Pragma": "no-cache",
                    "Referer": "http://m.ip138.com/",
                }
                resp = requests.get(url="http://www.1356789.com/", proxies=proxies, headers=headers, timeout=10)
                if resp.status_code == 200:
                    page = resp.text
                    ip_url = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', page).group()
                    ip_now = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', ip_proxy).group()
                    if ip_url == ip_now:  # 判断是否是匿名代理
                        self.ip_valid.append(ip_proxy + " " + ip_site + " 匿名代理")
                        print(ip_proxy + " " + ip_site +  " 匿名代理")
                    else:
                        self.ip_valid.append(ip_proxy + " " + ip_site +  " 透明代理")
                        print(ip_proxy + " " + ip_site +  " 透明代理")
            except Exception as e:
                print(ip_proxy + " 该代理ip无效或响应过慢！")


if __name__ == "__main__":
    ip = ProxyIp.get_proxy_ip()
    f = open("ip.txt", "w")
    for i in ip:
        try:
            f.write(i + "\n")
        except Exception as e:
            print(e)
    f.close()
