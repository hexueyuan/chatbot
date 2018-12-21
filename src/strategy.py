# -*- coding:utf8 -*-

import os
import re
import itchat
import time
import random
import subprocess

import hat
import webcrawl
import download
import logger as log

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
    flag = True
    #个人注册函数触发检测
    user = itchat.search_friends(userName=msg["FromUserName"])
    if user is not None and user["NickName"].encode("utf-8") == username:
        for key, func in strategy_map_me.items():
            key_com = re.compile(key)
            if key_com.match(text) and flag:
                func(msg, isGroupChat)
                flag = False
    #群消息注册函数触发检测
    if isGroupChat and msg.isAt:
        for key, func in strategy_map_chatroom.items():
            key_com = re.compile(key)
            if key_com.match(text) and flag:
                func(msg, isGroupChat)
                flag = False
    #私聊消息注册函数触发检测
    else:
        for key, func in strategy_map_chatone.items():
            key_com = re.compile(key)
            if key_com.match(text) and flag:
                func(msg, isGroupChat)
                flag = False

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
    msg = "{} -> {} : {}".format(fromUserName, toUserName, msg["Content"].encode("utf8"))
    log.info(msg.decode("utf8"))

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
        log.info(("save image to " + image_path).decode("utf8"))
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
        log.info("未找到匹配图片".decode("utf8"))
        image_path = no_image_result_path
    elif image_url == "trigger_blackword":
        log.info(("触发黑名单词：" + query).decode("utf8"))
        image_path = warning_image_path
    else:
        image_path = download.download_image(image_url)
        log.info(("save image to " + image_path).decode("utf8"))
    msg.user.send_image(image_path)

#动态添加黑名单词
def add_blackword(msg, isGroupChat=False):
    query = msg.get("Text", u"").encode("utf-8").replace("黑名单词：", "").strip()
    _chat_log(msg, isGroupChat)
    if query != "":
        blackword_list.append(query)

def christmas_hat(msg, isGroupChat=False):
    _chat_log(msg, isGroupChat)
    hat_img_path_list = [
        "../static/hat/hat.png"
    ]
    username = msg.get("FromUserName", "")
    if username == "":
        log.info("[fail] get user info fail!")
        msg.user.send(u"机器人小源提示: 无法获取您的用户信息!")
    head_img = itchat.get_head_img(username)
    if head_img is None:
        log.info("[fail] get head face fail!")
        msg.user.send(u"机器人小源提示: 获取您的头像图片失败!")
    head_img_path = "../image/" + str(int(time.time())) + ".jpg"
    with open(head_img_path, "wb") as f:
        f.write(head_img)
    hat_img_path = random.choice(hat_img_path_list)
    head_with_hat_img_path = hat.add_hat(head_img_path, hat_img_path)
    if head_with_hat_img_path is None:
        log.info("[fail] no people face in head image!")
        msg.user.send(u"机器人小源提示: 您的头像中未能识别出人脸，可能是小源还不支持识别动漫人脸哦~")
    else:
        log.info("[success] merge hat and head image to " + head_with_hat_img_path)
        msg.user.send_image(head_with_hat_img_path)

def tail_log(msg, isGroupChat=False):
    _chat_log(msg, isGroupChat)
    query = int(msg.get("Text", u"").encode("utf-8").replace("日志：", "").strip())
    subshell = subprocess.Popen(args="tail -n {} ../log/chatbot.log".format(query), shell=True, env=None, stdout=subprocess.PIPE)
    text = subshell.stdout.read()
    subshell.stdout.close()
    msg.user.send(text.decode("utf8"))

def get_image(msg, isGroupChat=False):
    _chat_log(msg, isGroupChat)
    query = msg.get("Text", u"").encode("utf-8").replace("图片：", "").strip()
    if not os.path.exists(query):
        msg.user.send(u"没有找到该图片")
    else:
        msg.user.send_image(query)

#所有用户私聊和群消息均可触发
#其它用户群消息必须@本用户触发
strategy_map_global = {
    "表情包$": send_emoji_chat,
    "表情包：.*$": send_emoji_chat_with_query
}

#所有用户群消息
#其它用户必须@本用户触发
strategy_map_chatroom = {}

#私聊
strategy_map_chatone = {
    "我要圣诞帽$": christmas_hat
}

#本用户消息触发
strategy_map_me = {
    "表情包$": send_emoji_chat,
    "表情包：.*$": send_emoji_chat_with_query,
    "黑名单词：.*$": add_blackword,
    "日志：.*$": tail_log,
    "图片：.*$": get_image
}
