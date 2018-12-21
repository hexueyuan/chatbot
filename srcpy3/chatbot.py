# -*- coding:utf8 -*-
#!/user/bin/env python

import itchat
import json
import strategy
import simple_log as log

@itchat.msg_register(itchat.content.TEXT)
def trigger_chatone(msg):
    strategy.strategy_switcher(msg, isGroupChat=False)

@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def trigger_chatroom(msg):
    strategy.strategy_switcher(msg, isGroupChat=True)

if __name__ == '__main__':
    log.init("../log/chatbot", "NOTICE")
    uuid = itchat.get_QRuuid()
    itchat.auto_login(hotReload=True, enableCmdQR=2) #如果命令行二维码显示不全，可以使用该行
    #itchat.auto_login(hotReload=True, enableCmdQR=True)
    strategy.init()

    itchat.run()

    strategy.exit()
    log.notice("程序退出")
