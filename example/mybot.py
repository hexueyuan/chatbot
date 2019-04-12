# -*- coding:utf-8 -*-
# python2

import sys

sys.path.append('../src')

import chatbot

botman = chatbot.chatbot()

@botman.listen('你好')
def hello():
    return '你好'

if __name__ == "__main__":
    botman.run()