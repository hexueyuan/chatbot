# -*- coding:utf8 -*-

import re
import itchat
import webcrawl
import download
import simple_log as log

username = ""
blackword_list = []
warning_image_path = "../static/warning.gif"
no_image_result_path = "../static/noimage.jpg"
blackword_file = "../static/blackword"

def init():
    global username
    global blackword_list
    with open(blackword_file) as f:
        for word in f:
            blackword_list.append(word.strip())
    me = itchat.search_friends()
    username = me.get("NickName", u"我").encode("utf-8")
    strategy_map_chatone.update(strategy_map_global)
    strategy_map_chatroom.update(strategy_map_global)

def exit():
    with open(blackword_file, "w+") as f:
        for word in blackword_list:
            f.write(word + '\n')

def strategy_switcher(msg, isGroupChat=False):
    text = ""
    if isGroupChat and msg.isAt:
        text = msg.text.split(u"\u2005", 2)[-1].encode("utf-8")
    else:
        text = msg.text.encode("utf-8")
    #个人注册函数触发检测
    user = itchat.search_friends(userName=msg["FromUserName"])
    if user is not None and user["NickName"].encode("utf-8") == username:
        for key, func in strategy_map_me.items():
            key_com = re.compile(key)
            if key_com.match(text):
                func(msg, isGroupChat)
    #群消息注册函数触发检测
    if isGroupChat and msg.isAt:
        for key, func in strategy_map_chatroom.items():
            key_com = re.compile(key)
            if key_com.match(text):
                func(msg, isGroupChat)
    #私聊消息注册函数触发检测
    else:
        for key, func in strategy_map_chatone.items():
            key_com = re.compile(key)
            if key_com.match(text):
                func(msg, isGroupChat)

#日志记录
def _chat_log(msg, isGroupChat=False):
    text = msg.get('Text', u"").encode("utf-8")
    #发送方
    fromUser = itchat.search_friends(userName=msg["FromUserName"])
    if fromUser is None:
        fromUserName = "Stranger"
    else:
        fromUserName = fromUser["NickName"].encode("utf8")
    #接收方
    if isGroupChat:
        toUser = itchat.search_chatrooms(userName=msg["ToUserName"])
    else:
        toUser = itchat.search_friends(userName=msg["ToUserName"])
    if toUser is None:
        toUserName = "Stranger"
    else:
        toUserName = toUser["NickName"].encode("utf8")
    log.notice("{} -> {} : {}".format(fromUserName, toUserName, msg["Content"].encode("utf8")))

#===========注册函数===========#

#无query模式，随机返回一张站点推荐图片
def send_emoji_chat(msg, isGroupChat=False):
    image_url = webcrawl.get_image_url()
    _chat_log(msg, isGroupChat)
    if image_url is None:
        log.debug("未找到匹配图片")
        image_path = no_image_result_path
    else:
        image_path = download.download_image(image_url)
    msg.user.send_image(image_path)

#带query模式，搜索query并返回结果中的一张图片
def send_emoji_chat_with_query(msg, isGroupChat=False):
    query = msg.get("Text", u"").encode("utf-8").replace("表情包：", "").strip()
    if query in blackword_list:
        image_url = "trigger_blackword"
    else:
        image_url = webcrawl.get_image_url_with_query(query)
    _chat_log(msg, isGroupChat)
    if image_url is None:
        log.debug("未找到匹配图片")
        image_path = no_image_result_path
    elif image_url == "trigger_blackword":
        log.notice("触发黑名单词：" + query)
        image_path = warning_image_path
    else:
        image_path = download.download_image(image_url)
    msg.user.send_image(image_path)

#动态添加黑名单词
def add_blackword(msg, isGroupChat=False):
    query = msg.get("Text", u"").encode("utf-8").replace("黑名单词：", "").strip()
    _chat_log(msg, isGroupChat)
    if query != "":
        blackword_list.append(query)

#所有用户私聊和群消息均可触发
#其它用户群消息必须@本用户触发
strategy_map_global = {
    #"表情包$": send_emoji_chat,
    #"表情包：.*$": send_emoji_chat_with_query
}

#所有用户群消息
#其它用户必须@本用户触发
strategy_map_chatroom = {}

#私聊
strategy_map_chatone = {}

#本用户消息触发
strategy_map_me = {
    "表情包$": send_emoji_chat,
    "表情包：.*$": send_emoji_chat_with_query,
    "黑名单词：.*$": add_blackword
}
