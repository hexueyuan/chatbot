# -*- coding:utf-8 -*-
# python2

import itchat
import logging
import threading
import collections

context = threading.local()
context.msg = None

msg = context.msg

class chatbot():
    nickName = "chatbot"
    userName = ""
    def __init__(self):
        """
        """
        self.listen_rule = {
            "onechat": collections.defaultdict(list), 
            "groupchat": collections.defaultdict(list), 
            "mechat": collections.defaultdict(list)
        }
        itchat.auto_login(hotReload=True)
        me = itchat.search_friends()
        self.nickName = me['NickName'].encode('utf-8')
        self.userName = me['UserName']
        logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.context = threading.local()

    def add_listen_rule(self, key_word, handler, isOne=True, isSelf=False, isGroup=False, isAt=False, nickName=None):
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

    def listen(self, key_word, isOne=True, isSelf=False, isGroup=False, isAt=False, nickName=None):
        """
        """
        def decorator(f):
            self.add_listen_rule(key_word, f, isOne, isSelf, isGroup, isAt, nickName)
            return f
        return decorator

    def get_from_username(self, msg, isGroupChat=False):
        """
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
        """
        if msg.get('User').has_key('Self') and msg['User']['Self']['DisplayName'].encode('utf-8') != '':
            return msg['User']['Self']['DisplayName'].encode('utf-8')
        else:
            return self.nickName

    def _get_rules(self):
        """
        """
        global context
        msg = context.msg

        text = msg["Text"].encode("utf-8")
        if context.isAt:
            prefix = '@' + self.get_group_selfname(msg) + ' '
            text = text.replace(prefix, '')
        self.logger.debug('关键词: ({})'.format(text))

        if context.fromUserNickName == self.nickName:
            self.logger.debug('检索个人规则词表')
            return self.listen_rule["mechat"].get(text, [])
        elif context.isGroupChat:
            self.logger.debug('检索群聊规则词表')
            return self.listen_rule["groupchat"].get(text, [])
        else:
            self.logger.debug('检索私聊规则词表')
            return self.listen_rule["onechat"].get(text, [])

    def _handler_one_rule(self, rule):
        """
        """
        global context
        msg = context.msg

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

    def _handler_diliver(self, msg, isGroupChat):
        """
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