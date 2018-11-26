# chatbot
微信表情包机器人

## 项目介绍  
本项目基于[itchat](https://github.com/littlecodersh/itchat)库进行开发，使用爬虫访问[bee-ji](http://www.bee-ji.com)网站获取表情包，仅娱乐非商用。  
项目后台启动后监听登录账号收发的消息，并捕捉如下指令。  
> 表情包  
> 表情包：关键词  
> 表情包:关键词  

支持群聊@账号加命令。  
使用见下图：
![群聊中使用](https://github.com/hexueyuan/chatbot/blob/master/static/qunliao.jpg)
![私聊中使用](https://github.com/hexueyuan/chatbot/blob/master/static/siliao.jpg)

## 下载
> git clone git@github.com:hexueyuan/chatbot.git
  
## 使用
> cd chatbot  
> . init.sh  

输出当前环境，当init.sh检查结果正常时  

> cd src  
> python chatbot  

然后会在命令行出现二维码，使用微信扫描登录之后，chatbot开始运行

## tips
static目录下blackword为黑名单词表，每一行为一个黑名单词，当用户关键词匹配黑名单词时，输出static/warning.gif图片，当用户关键词没有找到相关图片时输出static/noimage.jpg，以上均可根据喜好修改。

2018-11-26 更新：
    重构命令注册方式，在strategy.py文件中四个全局map变量注册命令和命令触发函数，便于扩展
    新增支持动态添加黑名单词，命令规则为：`黑名单词：关键词`
