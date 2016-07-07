# coding:utf-8
import tempfile
from os import path

import time

import tornado
from PIL import Image

from view import View, route


@route("/uploadimg", name="uploadimg")
class UploadImg(View):
    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
        time.sleep(5)
        self.write(
            "<html><body><form action='/uploadimg' method='post' enctype='multipart/form-data' ><input name='uploadimg' type='file' /><input type='submit' value='提交' /></form></body></html>"
        )
        self.finish()

    '''
    文件上传的内容体在tornado.web.RequestHandler.request.files属性中，并且是以数组形式存放的。
    使用临时文件存储时，在write完成后要记着把seek重置到文件头。要不然文件无法被读取。
    再使用Image模块的thumbnail方法进行缩放时,resample=1作为重载渲染参数能够有效的使图片平滑，消除锯齿。
    '''
    def post(self, *args, **kwargs):
        upload_path = path.join(path.dirname(path.abspath(__file__)), '../static/img/upload')
        if self.request.files != {}:
            metas = self.request.files['uploadimg']
            for meta in metas:
                rawname = meta['filename']
                dstname = str(int(time.time())) + '.' + rawname.split('.').pop()
                thbname = "thumb_" + dstname
                tf = tempfile.NamedTemporaryFile()
                tf.write(meta["body"])
                tf.seek(0)
                print(tf.name)

                img = Image.open(tf.name)
                img.thumbnail((920, 920), resample=1)
                img.save(path.join(upload_path, dstname))

                img.thumbnail((100, 100), resample=1)
                img.save(path.join(upload_path, thbname))
                self.write("finished!")

    def write_error(self, status_code, **kwargs):
        if status_code == 403:
            self.write("403.html")
