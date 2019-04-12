# -*- coding:utf-8 -*-

import itchat
import logging
import threading
import collections
import re

context = threading.local()
context.msg = None

msg = context.msg

class Chatbot():
    nickName = "chatbot"
    userName = ""
    def __init__(self, conf=None):
        """
        init methods.
            initialize listen rule, there are three element in it, `onechat`, `groupchat` and
            `mechat`, onechat means private chat, groupchat means a chatroom, mechat means self
            word content.All the rules defined will store in this dict, and in order to reduce 
            code logic to set these three value as defaultdict.

            login wechat client.it set hotReload as True, so you can login without scan QR image
            agin and agin.

            get your information such as nickName and userName, nick name is different from username
            refer from itchat document and itchat support using username to search user information.

            initialize logger module.chatbot use python `logging` module to note the important data.

            initialize chat context.Chat context store the message object and it's relative independence
            in different threading.
        """
        # listen_rule
        # store your listen rules
        # you can add new rule by using `listen` methods or `add_listen_rule` method
        self.listen_rule = {
            "onechat": collections.defaultdict(list), 
            "groupchat": collections.defaultdict(list), 
            "mechat": collections.defaultdict(list)
        }

        # login to wechat client
        # TODO: make it configurable, and provide more configure options
        # set default hotReload as True to decrease login time
        if conf is not None:
            login_conf = conf.get('login_conf', {})
        else:
            login_conf = {}
        hotReload           = login_conf.get('hotReload',           False)
        statusStorageDir    = login_conf.get('statusStorageDir',    'chatbot.pkl')
        enableCmdQR         = login_conf.get('enableCmdQR',         False)
        picDir              = login_conf.get('picDir',              None)
        qrCallback          = login_conf.get('qrCallback',          None)
        loginCallback       = login_conf.get('loginCallback',       None)
        exitCallback        = login_conf.get('exitCallback',        None)
        itchat.auto_login(
                        hotReload       =   hotReload, 
                        statusStorageDir=   statusStorageDir,
                        enableCmdQR     =   enableCmdQR,
                        picDir          =   picDir,
                        qrCallback      =   qrCallback,
                        loginCallback   =   loginCallback,
                        exitCallback    =   exitCallback)

        # initialize self information
        # itchat provide `search_friends` methods to search user information by user name
        # if no user name support it return your own infomation, it is useful so save it.
        me = itchat.search_friends()
        self.nickName = me['NickName'].encode('utf-8')
        self.userName = me['UserName']

        # initialize logger module
        # it's important to log while the program is running, chatbot use logging module to
        # log the important data, and it send to stout device
        # TODO: log configurable
        if conf is not None:
            logger_conf = conf.get('logger_conf', {})
        else:
            logger_conf = {}
        level   = logger_conf.get('level',  'DEBUG')
        format  = logger_conf.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        name    = logger_conf.get('name',   __name__)
        path    = logger_conf.get('path',   None)

        if level.upper() == "INFO":
            level = logging.INFO
        elif level.upper() == "WARNING":
            level = logging.WARNING
        elif level.upper() == "ERROR":
            level = logging.ERROR
        elif level.upper() == "FATAL":
            level = logging.FATAL
        else:
            level = logging.DEBUG

        logging.basicConfig(level=level, format=format, filename=path)
        self.logger = logging.getLogger(name)

    def add_listen_rule(self, key_word, handler, isOne=True, isSelf=False, isGroup=False, isAt=False, nickName=None):
        """
        add_listen_rule
            add a rule to chatbot.
        """
        listen_rule = self.listen_rule
        
        rules_box = []
        if isSelf:
            rules_box.append(listen_rule["mechat"])
        if isGroup:
            rules_box.append(listen_rule["groupchat"])
        if isOne:
            rules_box.append(listen_rule["onechat"])

        for rules in rules_box:
            rule = {
                "handler": handler,
                "handlerName": handler.__name__,
                "isAt": isAt
            }
            if nickName is not None:
                rule['nickName'] = nickName
            rules[key_word].append(rule)

    def listen(self, key_word, isOne=False, isSelf=False, isGroup=False, isAt=False, nickName=None):
        """
        add listen rule by decorator
        """
        if not isOne and not isSelf and not isGroup:
            isOne = True
        def decorator(f):
            self.add_listen_rule(key_word, f, isOne, isSelf, isGroup, isAt, nickName)
            return f
        return decorator

    def get_from_username(self, msg, isGroupChat=False):
        """
        get msg sender nickname
        """
        if isGroupChat:
            return msg['ActualNickName'].encode('utf-8')

        friend = itchat.search_friends(userName=msg["FromUserName"])
        if friend is None:
            return "未知"
        else:
            return friend['NickName'].encode("utf-8")

    def get_group_selfname(self, msg):
        """
        get your nickname in a centain group
        """
        if msg.get('User').has_key('Self') and msg['User']['Self']['DisplayName'].encode('utf-8') != '':
            return msg['User']['Self']['DisplayName'].encode('utf-8')
        else:
            return self.nickName

    def _get_rules(self):
        """
        get the rules base on context.
        """
        global context
        msg = context.msg

        text = msg["Text"].encode("utf-8")
        if context.isAt:
            prefix = '@' + self.get_group_selfname(msg) + ' '
            text = text.replace(prefix, '')
        self.logger.debug('关键词: ({})'.format(text))

        rules = []
        aim_rules = None
        if context.fromUserNickName == self.nickName:
            self.logger.debug('检索个人规则词表')
            aim_rules = self.listen_rule['mechat']
        elif context.isGroupChat:
            self.logger.debug('检索群聊规则词表')
            aim_rules =  self.listen_rule["groupchat"]
        else:
            self.logger.debug('检索私聊规则词表')
            aim_rules =  self.listen_rule["onechat"]

        for key, value in aim_rules.items():
            key_com = re.compile(key)
            if key_com.match(text):
                rules.extend(value)
        return rules

    def _handler_one_rule(self, rule):
        """
        running a handler rule
        """
        self.logger.info("触发处理函数: {}".format(rule['handlerName']))
        global context
        msg = context.msg

        if not context.isGroupChat:
            rule['isAt'] = False

        if rule['isAt'] == context.isAt and rule.get('nickName', context.fromUserNickName) == context.fromUserNickName:
            handler = rule['handler']
            content = handler()

            if type(content) == type(str()):
                self.logger.debug("返回信息: {}".format(content))
                msg.User.send(content.decode('utf-8'))
            elif type(content) == type(tuple()):
                t, arg = content
                if t == "text":
                    self.logger.debug("返回信息: {}".format(arg))
                    msg.User.send(arg.decode('utf-8'))
                elif t == "image":
                    self.logger.debug("返回图片: {}".format(arg))
                    msg.User.send_image(arg)
                else:
                    self.logger.debug("未支持返回类型: {}".format(t))
            else:
                self.logger.warning("处理函数返回格式错误，错误类型: {}".format(str(type(content))))
        else:
            self.logger.info("处理函数配置项匹配失败")
            if rule['isAt'] != context.isAt:
                self.logger.debug("群聊@属性不匹配")
                self.logger.debug("{} != {}".format(str(rule['isAt']), str(context.isAt)))
            if rule.get('nickName', context.fromUserNickName) != context.fromUserNickName:
                self.logger.debug("对象昵称不匹配")
                self.logger.debug("{} != {}".format(rule.get('nickName', context.fromUserNickName), context.fromUserNickName))

    def _handler_diliver(self, msg, isGroupChat):
        """
        while msg is comming, check it and return
        """
        global context
        context.msg = msg
        context.isGroupChat = isGroupChat
        context.isAt = msg.get('isAt', False)
        context.fromUserNickName = self.get_from_username(msg)

        rules = self._get_rules()

        self.logger.info("触发规则: {} 条".format(len(rules)))
        
        for rule in rules:
            self._handler_one_rule(rule)

    def run(self):
        """
        run chatbot
        """
        @itchat.msg_register(itchat.content.TEXT)
        def trigger_chatone(msg):
            fromUserName = self.get_from_username(msg)
            text = msg['Text'].encode('utf-8')
            self.logger.info('(普通消息){}: {}'.format(fromUserName, text))
            
            t = threading.Thread(target=self._handler_diliver, args=(msg, False))
            t.setDaemon(True)
            t.start()

        @itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
        def trigger_chatgroup(msg):
            fromUserName = self.get_from_username(msg, isGroupChat=True)
            text = msg['Text'].encode('utf-8')
            self.logger.info('(群消息){}: {}'.format(fromUserName, text))

            t = threading.Thread(target=self._handler_diliver, args=(msg, True))
            t.setDaemon(True)
            t.start()
        
        itchat.run()