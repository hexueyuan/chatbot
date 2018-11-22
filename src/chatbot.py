# -*- coding:utf8 -*-
#!/user/bin/env python

import itchat
import webcrawl
import download
import json
import simple_log as log

username = ""
blackword_list = []
warning_image_path = "../static/warning.gif"
no_image_result_path = "../static/noimage.jpg"

#msg为消息内容
def handle_user_msg(text, msgObj):
    if text == "表情包":
        image_url = webcrawl.get_image_url()
    elif text.startswith("表情包:") or text.startswith("表情包："):
        #特地匹配了中文冒号和英文冒号
        query = text.replace("表情包：", "").replace("表情包:", "").strip()
        if query in blackword_list:
            log.debug("触发黑名单词:" + query)
            image_url = "warning"
        else:
            image_url = webcrawl.get_image_url_with_content(query)
    else:
        return
    if image_url == "warning":
        image_path = warning_image_path
    elif image_url is not None:
        image_path = download.download_image(image_url)
    else:
        log.debug("未找到相关图片")
        image_path = no_image_result_path
    msgObj.user.send_image(image_path)
    log.debug("Send image success")

@itchat.msg_register(itchat.content.TEXT)
def print_content(msg):
    text = msg['Text'].encode("utf-8")
    user = msg['User']['UserName']
    fromUser = itchat.search_friends(userName=msg["FromUserName"])
    if fromUser is None:
        fromUserName = "Stranger"
    else:
        fromUserName = fromUser["NickName"].encode("utf8")
    toUser = itchat.search_friends(userName=msg["ToUserName"])
    if toUser is None:
        toUserName = "Stranger"
    else:
        toUserName = toUser["NickName"].encode("utf8")
    if toUser is None:
        toUser = {}
    log.notice("{} -> {} : {}".format(fromUserName, toUserName, msg["Content"].encode("utf8")))
    handle_user_msg(text, msg)

@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def text_reply(msg):
    fromUser = itchat.search_friends(userName=msg["FromUserName"])
    if fromUser is None:
        fromUser = {}
    toChatroom = itchat.search_chatrooms(userName=msg["ToUserName"])
    if toChatroom is None:
        toChatroom = {}
    log.notice("{} -> {} : {}".format(fromUser.get("NickName", u"Stranger").encode("utf-8"), 
        toChatroom.get("NickName", u"Stranger").encode("utf-8"), msg["Content"].encode("utf-8")))
    if msg.isAt:
        text = msg.text.replace(username, u"").split(u"\u2005", 2)[-1].encode("utf-8")
        handle_user_msg(text, msg)
    elif fromUser is not None and fromUser.get("NickName", "") == username:
        text = msg.text.encode("utf-8")
        handle_user_msg(text, msg)

if __name__ == '__main__':
    log.init("../log/chatbot", "notice")
    uuid = itchat.get_QRuuid()
    itchat.auto_login(hotReload=True)
    me = itchat.search_friends()
    username = me["NickName"]
    #加载黑名单词
    with open("../static/blackword") as f:
        for word in f:
            blackword_list.append(word.strip())

    itchat.run()
