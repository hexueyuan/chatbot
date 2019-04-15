# -*- coding:utf-8 -*-

import sys
import itchat
import time

import hat
sys.path.append('../../src')

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
        "path": "./christmas_hat_robot.log",
        "name": "christmas_hat_robot",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "level": "INFO"
    }
}
robot = Chatbot(conf=config)

@robot.listen('我要圣诞帽', isOne=True, isGroup=True, isSelf=True, isAt=True)
def christmas_hat():
    hat_path = 'static/hat.png'
    # 获取用户头像
    head_img_content = itchat.get_head_img(context.msg['FromUserName'])
    head_img_path = 'img/headImg' + str(int(time.time())) + '.jpg'
    with open(head_img_path, 'wb') as f:
        f.write(head_img_content)
    # 合成图像
    combine_img_path = hat.add_hat(head_img_path, hat_path)
    if combine_img_path is None:
        return "失败了，可能是头像还不够清晰，检测不到人脸:("
    return "image", combine_img_path

if __name__ == "__main__":
    robot.run()