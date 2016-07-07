# coding:utf-8
import json
import re
import requests
import time
from lxml import etree
from model.xpinyin import Pinyin


class GetWeather:
    @classmethod
    def by_ip138(cls, ip=''):
        get_url = 'http://www.ip138.com/ips138.asp?ip=' + ip + '&action=2'
        url = 'http://www.ip138.com'
        ip138 = requests.session()
        ip138.get(url)
        response = ip138.get(url=get_url)
        page = etree.HTML(response.content)
        p = page.xpath("//ul[@class='ul1']/li[1]/text()")
        s = re.search(r'本站主数据：(.+)省(.+)市', p[0])
        if s is not None:
            site_province = s.group(1)
            site_city = s.group(2)
            site = {"province": site_province, "city": site_city}
        else:
            s = re.search(r'本站主数据：(.+) ', p[0]).group(1)
            site = {"country": s}
        return site

    @classmethod
    def by_ip(cls, ip):
        r = requests.get("http://ip.taobao.com/service/getIpInfo.php?ip=" + ip)
        ip_return = json.loads(r.text)
        if ip_return["code"] == 0:
            province = ip_return["data"]["region"]
            city = ip_return["data"]["city"]
            province = province.replace("省", "")
            province = province.replace("市", "")
            city = city.replace("市", "")
            site = {"province": province, "city": city}

            return site

    @classmethod
    def get_weather_24(cls, town_id):  # town_id需要自己到天气网上找，地址栏那边，很好找
        observe24h_url = "http://www.weather.com.cn/weather1d/" + town_id + ".shtml#dingzhi_first"
        response = requests.get(url=observe24h_url)
        page = etree.HTML(response.content)
        p = page.xpath("//script")
        data_rep = re.sub("(var observe24h_data = )|;", "", p[8].text)  # 将没用的字符去掉才能进行下一步
        data_json = json.loads(data_rep)
        observe24h_data = {}
        k = 0
        for i in data_json['od']['od2'][::-1]:  # 挑了一些有用的信息出来，我是用小时来作用字典的键值，因为一天24小时头和尾的小时数是一样的，所以多了一个参数k来区分
            if k <= 9:
                k = "0" + str(k)
            else:
                k = str(k)
            observe24h_data[i["od21"] + "h" + k] = {"temp": i["od22"], "wind_type": i["od24"], "wind_level": i["od25"],
                                                    "rain": i["od26"], "humidity": i["od27"]}
            k = int(k)
            k += 1
        observe24h_data["town"] = data_json["od"]["od1"]
        return observe24h_data

    @classmethod
    def get_weather_now(cls, town_id):
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",

            "Host": "d1.weather.com.cn",
            "Referer": "http://www.weather.com.cn/weather1d/" + town_id + ".shtml"
        }
        observe_now_url = "http://d1.weather.com.cn/sk_2d/" + town_id + ".html?_=" + str(int(time.time() * 1000))
        response = requests.get(observe_now_url, headers=headers)
        data_rep = re.sub("(var dataSK = )|;", "", response.content.decode())
        data_json = json.loads(data_rep)
        observe_now_data = {}
        observe_now_data["所在地"] = data_json["cityname"]
        observe_now_data["今天"] = data_json["date"]
        observe_now_data["更新时间"] = data_json["time"]
        observe_now_data["温度"] = data_json["temp"]
        observe_now_data["湿度"] = data_json["SD"]
        observe_now_data["降水量"] = data_json["rain"]
        observe_now_data["风力"] = data_json["WS"]
        observe_now_data["风向"] = data_json["WD"]
        return observe_now_data

    @classmethod
    def get_weather_de(cls, town_id):
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",

            "Host": "d1.weather.com.cn",
            "Referer": "http://www.weather.com.cn/weather1d/" + town_id + ".shtml"
        }
        observe_de_url = "http://d1.weather.com.cn/dingzhi/" + town_id + ".html?_=" + str(int(time.time() * 1000))
        response = requests.get(observe_de_url, headers=headers)
        data_rep = re.sub("(var cityDZ([0-9]+) =)", "[", response.content.decode())
        data_rep = re.sub("(;var alarmDZ([0-9]+) =)", ",", data_rep)
        data_rep += "]"
        data_json = json.loads(data_rep)
        weatherinfo = {}
        weatherinfo["温度"] = data_json[0]["weatherinfo"]["temp"] + "/" + data_json[0]["weatherinfo"]["tempn"]
        weatherinfo["天气"] = data_json[0]["weatherinfo"]["weather"]
        weatherinfo["风力"] = data_json[0]["weatherinfo"]["ws"]
        weatherinfo["风向"] = data_json[0]["weatherinfo"]["wd"]
        weatherinfo["预警"] = {}
        try:
            x = 0
            for i in data_json[1]:
                for k in data_json[1][i]:
                    weatherinfo["预警"][x] = k["w8"] + ":" + k["w9"]
                    x += 1
        except Exception as e:
            print(e)
        return weatherinfo

    @classmethod
    def get_weather_sug(cls, town_id):
        suggest_url = "http://www.weather.com.cn/weather1d/" + town_id + ".shtml#dingzhi_first"
        response = requests.get(url=suggest_url)
        page = etree.HTML(response.content)
        suggest_info = {}
        for i in range(5):
            em = page.xpath("//div[@class='livezs']/ul[@class='clearfix']/li/em")
            span = page.xpath("//div[@class='livezs']/ul[@class='clearfix']/li/span")
            p = page.xpath("//div[@class='livezs']/ul[@class='clearfix']/li/p")
            suggest_info[em[i].text] = span[i].text + "," + p[i].text
        return suggest_info

    @classmethod
    def get_town(cls, site):
        p = Pinyin()
        site_city = p.get_pinyin(site["city"], '')
        site_province = p.get_initials(site["province"], '').lower()
        url = 'http://www.weather.com.cn'
        get_url = 'http://' + site_province + '.weather.com.cn/' + site_city + '/index.shtml'
        weather = requests.session()
        weather.get(url=url)
        response = weather.get(url=get_url)
        page = etree.HTML(response.content)
        p = page.xpath("//div[@id='forecastID']/dl/dt/a")
        town = {}
        for i in p:
            size_href1 = i.get('href')
            town_id = re.search(r'weather/([0-9]+)', size_href1).group(1)
            town_name = i.text
            town[town_name] = town_id
        return town, site

    @classmethod
    def get_weather(cls, ip):
        site = cls.by_ip(ip)
        p = Pinyin()
        site_city = p.get_pinyin(site["city"], '')
        site_province = p.get_initials(site["province"], '').lower()
        url = 'http://www.weather.com.cn'
        get_url = 'http://' + site_province + '.weather.com.cn/' + site_city + '/index.shtml'
        weather = requests.session()
        weather.get(url=url)
        response = weather.get(url=get_url)
        page = etree.HTML(response.content)
        p = page.xpath("//div[@id='forecastID']/dl/dt/a")[0]
        href = p.get("href")
        town_id = re.search(r'weather/([0-9]+)', href).group(1)
        suggest_info = cls.get_weather_sug(town_id)
        now_info = cls.get_weather_now(town_id)
        detail_info = cls.get_weather_de(town_id)
        now_info["温度差"] = detail_info["温度"]
        now_info["天气"] = detail_info["天气"]
        return suggest_info, now_info


if __name__ == "__main__":
    w = GetWeather.get_weather('115.168.76.177')
    print(w)
