# chatbot
微信机器人
基于itchat的微信机器人框架，把自己的微信号变成一个智能机器人。

---

## 项目介绍  
本项目基于[itchat](https://github.com/littlecodersh/itchat)库进行开发，启动之后机器人监听私聊和群聊消息，当匹配文字指令之后，执行机器人服务。  

---
目前实现了两个服务：  
 1. 微信表情包  
使用爬虫访问[bee-ji](http://www.bee-ji.com)网站获取表情包，仅娱乐非商用。  
项目后台启动后监听登录账号收发的消息，并捕捉如下指令。  
> 表情包  
> 表情包：关键词  
> 表情包:关键词  

群聊消息需要@账号加指令。  
使用见下图:
![群聊中使用](/static/qunliao.jpg)  

![私聊中使用](/static/siliao.jpg)

为了防止用户恶意某些不当到关键词，添加了黑名单词表，当触发黑名单词时，返回自定义图片。
static目录下blackword为黑名单词表，每一行为一个黑名单词，当用户关键词匹配黑名单词时，输出static/warning.gif图片，当用户关键词没有找到相关图片时输出static/noimage.jpg，以上均可根据喜好修改。

2. 我要圣诞帽
基于dlib的人脸识别和opencv的图像处理，微信机器人监听好友私聊信息，识别到`我要圣诞帽`指令时，获取好友头像并添加圣诞帽，然后返回合成后到图片给好友。
![我要圣诞帽](/static/chrismashat.jpg)

---

## 下载
> git clone git@github.com:hexueyuan/chatbot.git
  
## 使用
> cd chatbot  
> . init.sh  

输出当前环境，当init.sh检查结果正常时(未添加opencv环境检查，请自行检查opencv环境)  

> cd src  
> python chatbot  

然后会在命令行出现二维码，使用微信扫描登录之后，chatbot开始运行

## 开发 
微信机器人可以很容易扩展其他到服务，比如你可以通过微信机器人传送远端文件，这样你可以通过手机和家里登录了微信机器人的电脑进行文件传送，也可以通过微信机器人开发智能聊天机器人等。  

微信机器人将添加新服务的过程进行了简单封装，在src/strategy.py程序中，有如下几个dict:
```python
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
    "黑名单词：.*$": add_blackword
}
```
这是服务注册的配置，若你需要增加一个新的服务，请按照已有的服务函数(send_emoji_chat、christmas_hat)写自己的服务函数，并添加到服务注册配置中，服务注册有四个注册体，分别监控`群聊中其他用户信息`、`私聊中他人的信息`、`群聊和私聊中本用户的信息`、`群聊和私聊中其他用户的信息`,参见代码中的注释部分，注册关键词为正则匹配模式。

以下提供一个开发样例，实现用户私聊发送`我的信息`时返回在itchat中查询到的好友信息。  
首先编写服务函数，这部分添加到strategy.py文件中:  
```python
import json

def send_user_info(msg, isGroup=False):
    info = itchat.search_friends(msg["FromUserName"]
    msg.user.send(json.dumps(info, indent=2, ensure_ascii=False))
```
函数很简单，当触发该服务时，获取msg中到user信息，并使用json库dump为字符串并返回给好友。接下来在私聊服务注册体中增加配置：  
```python
strategy_map_chatone = {
    "我要圣诞帽$": christmas_hat,
    "我的信息$": send_user_info
}
```
注册完成之后重新登录chatbot即可。
