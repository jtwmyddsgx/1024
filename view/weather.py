# coding: utf-8
import re
import tornado
from model.weather import GetWeather
from view import LoginView, route, View
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor


@route('/weather', name='weather')
class Weather(View):
    executor = ThreadPoolExecutor(2)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        xff = self.request.headers["X-Forwarded-For"]
        xff_re = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', xff)
        if xff_re is not None:
            remoteip = xff_re.group()
        else:
            remoteip = self.request.headers["X-Real-Ip"]
        # remoteip = '115.168.76.177'
        now_info = {}
        suggest_info = {}
        try:
            suggest_info, now_info = yield self.get_weather(remoteip)
        except Exception as e:
            print(e)
        self.render(
            'weather.html',
            now_info=now_info,
            suggest_info=suggest_info,
            page_title="天气",
        )

    @run_on_executor
    def get_weather(self, ip):
        return GetWeather.get_weather(ip)


@route('/weatherr', name='weatherr')
class Weatherr(LoginView):
    executor = ThreadPoolExecutor(4)

    def get(self):
        self.redirect('/town')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        town_id = self.get_argument('town_id', '')
        observe_now_data = {}
        weather_info = {}
        suggest_info = {}
        hour = []
        temp = []
        rain = []
        humidity = []
        wind_type = []
        wind_level = []
        town = ''
        try:
            observe24h_data = yield self.get_weather_24(town_id)
            observe_now_data = yield self.get_weather_now(town_id)
            weather_info = yield self.get_weather_de(town_id)
            suggest_info = yield self.get_weather_sug(town_id)
            for x in range(0, 25):
                for i in observe24h_data:
                    if i == "town":
                        pass
                    elif int(i[-2:]) == x:
                        hour.append(i[0:2])
                        temp.append(observe24h_data[i]['temp'])
                        rain.append(observe24h_data[i]['rain'])
                        humidity.append(observe24h_data[i]['humidity'])
                        wind_type.append(observe24h_data[i]['wind_type'])
                        wind_level.append(observe24h_data[i]['wind_level'])
            town = observe24h_data["town"]
        except Exception as e:
            print(e)
        self.render(
            'weather.html',
            hour=hour,
            temp=temp,
            rain=rain,
            humidity=humidity,
            wind_type=wind_type,
            wind_level=wind_level,
            town=town,
            observe_now_data=observe_now_data,
            weather_info=weather_info,
            suggest_info=suggest_info,
        )

    @run_on_executor
    def get_weather_24(self, size):
        return GetWeather.get_weather_24(size)

    @run_on_executor
    def get_weather_now(self, size):
        return GetWeather.get_weather_now(size)

    @run_on_executor
    def get_weather_de(self, size):
        return GetWeather.get_weather_de(size)

    @run_on_executor
    def get_weather_sug(self, size):
        return GetWeather.get_weather_sug(size)


@route('/town', name='town')
class GetTown(LoginView):
    executor = ThreadPoolExecutor(2)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        remoteip = self.request.remote_ip
        town = []
        site = []
        remoteip = '115.168.76.177'
        try:
            town, site = yield self.get_down(remoteip)
        except Exception as e:
            print(e)
        self.render(
            'get_town.html',
            site=site,
            town=town,
        )

    @run_on_executor
    def get_down(self, ip):
        site = GetWeather.by_ip(ip)
        return GetWeather.get_town(site)
