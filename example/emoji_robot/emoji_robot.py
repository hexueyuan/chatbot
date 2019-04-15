# -*- coding:utf-8 -*-
# python2

import sys
import urllib
import json
import random
import time
import requests

try:
    import urllib2 as requestlib
except ImportError:
    import urllib.request as requestlib

try:
    import cookielib as cookielib
except ImportError:
    import http.cookiejar as cookielib

<<<<<<< HEAD:example/emoji_robot/emoji_robot.py
sys.path.append('../../src')
=======
sys.path.append('../src')
>>>>>>> 56d84344ab1359d059bccefd5417b1c5647b2b30:example/emoji_robot.py

from chatbot import Chatbot, context

config = {
    "login_conf": {
        "hotReload": True,
        "statusStorageDir": 'chatbot.pkl',
        "enableCmdQR": False,
        "picDir": None,
        "qrCallback": None,
        "loginCallback": None,
        "exitCallback": None
    },
    "logger_conf": {
        "path": "./chat_robot.log",
        "name": "chat_robot",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "level": "DEBUG"
    }
}

robot = Chatbot(conf=config)

def emoji_image():
    cj = cookielib.LWPCookieJar()
    cookie_support = requestlib.HTTPCookieProcessor(cj)
    opener = requestlib.build_opener(cookie_support, requestlib.HTTPHandler)
    requestlib.install_opener(opener)

    user_agent = 'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1'
    cookie = "Hm_lvt_65e796f34b9ee7170192209a91520a9a=1555081237; Hm_lpvt_65e796f34b9ee7170192209a91520a9a=1555081315"
    url = 'http://www.bee-ji.com/data/search/json'
    image_base_url = "http://image.bee-ji.com/"
    image_path = './img/'

    req = requestlib.Request(url)
    req.add_header('User-Agent', user_agent)
    req.add_header('Cookie', cookie)
    data = opener.open(req).read()
    items = json.loads(data)
    if len(items) == 0:
        robot.logger.warning("未抓取到图片")
        return "哦豁，没了"
    
    image_item = random.choice(items)
    image_url = image_base_url + str(image_item['id'])
    robot.logger.info("获取图片url: {}".format(image_url))
    
    path = image_path + str(int(time.time()))
    rsp = requests.get(image_url)
    with open(path, "wb") as f:
        f.write(rsp.content)
    robot.logger.info("图片保存路径: {}".format(path))
    return 'image', path

if __name__ == "__main__":
    robot.add_listen_rule('我要表情包', emoji_image, isOne=True, isGroup=True, isSelf=True, isAt=True)
    robot.run()
    