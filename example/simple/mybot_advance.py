# -*- coding:utf-8 -*-

import sys

sys.path.append('../src')

from chatbot import Chatbot, context

#配置
conf = {
    "login_conf": {
        "hotReload": True
    }
}
botman = Chatbot(conf=conf)

# 返回对方的用户名
@botman.listen('你好')
def hello():
    fromUserName = botman.get_from_username(context.msg)
    return "你好，{}".format(fromUserName)

# 匹配正则
@botman.listen('大写:[a-zA-Z]*$')
def upword():
    text = context.msg.Text.encode('utf-8')
    text.replace('大写:', '')
    return text.upper()

if __name__ == "__main__":
    botman.run()