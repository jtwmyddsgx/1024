# coding:utf-8
from view import route, View


@route("/mytest",name="mytest")
class MyTest(View):
    def get(self, *args, **kwargs):
        self.write(str(self.request) + "\n")
        self.finish()
