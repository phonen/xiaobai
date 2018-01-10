#!/usr/bin/env python3
# coding: utf-8

from wxpy import *
import re
import requests
import json
import time
import os
import configparser
from wxpy.utils import start_new_thread
from OkcoinSpotAPI import OKCoinSpot

# from OkcoinFutureAPI import OKCoinFuture
# import chbtc_api

'''
使用 cache 来缓存登陆信息，同时使用控制台登陆
'''
bot = Bot('bot.pkl', console_qr=True)

'''
开启 PUID 用于后续的控制
'''
bot.enable_puid('wxpy_puid.pkl')

myconfig = {'site_url': 'http://13bag.com/'}
tuling_switch = False

config = configparser.ConfigParser()
config.read("conf.ini")

'''
邀请信息处理
'''
rp_new_member_name = (
    re.compile(r'^"(.+)"通过'),
    re.compile(r'邀请"(.+)"加入'),
)

'''
为保证兼容，在下方admins中使用标准用法
在 admin_puids 中确保将机器人的puid 加入
机器人的puid 可以通过 bot.self.puid 获得
其他用户的PUID 可以通过 执行 export_puid.py 生成 data 文件，在data 文件中获取
'''
admin_names = [
    u'杨祥贵',
    u'遥远的眼神'
]
'''
定义需要管理的群
群的PUID 可以通过 执行 export_puid.py 生成 data 文件，在data 文件中获取
'''
group_names = (
    u'比特股大户内部交流群',
)
alert_group = "比特股大户内部交流群"
# 格式化 Group
groups = list(map(lambda x: bot.groups().search(x)[0], group_names))
# 格式化 Admin
# admins = list(map(lambda x: bot.friends().search(puid=x)[0], admin_puids))

# 新人入群的欢迎语
welcome_text = '''🎉 欢迎 @{} 的加入！
😃 加我好友有惊喜！找优惠，找产品，有免单！
'''

invite_text = """欢迎您，我是机器人小白。
😃 我是你的机器人好友，输入：找XXX;就会得到你想要的天猫优惠券产品！
我是你的机器人好友，发送要买的淘宝产品链接给我，我会帮你找出产品优惠券发给你哦！
"""
'''
设置比特币行情关键字
'''
keyword_of_hqapi = {
    "btc": "okcoin",
    "ltc": "okcoin",
    "eth": "okcoin",
    "etc": "chbtc",
    "bts": "chbtc"
}

'''
设置群组关键词和对应群名
* 关键词必须为小写，查询时会做相应的小写处理
'''
keyword_of_group = {
    "lfs": "Linux中国◆LFS群",
    "dba": "Linux中国◆DBA群"
}

# 查询订单：*1234567890
order_id = re.compile(r'^(?:\*(\d{16,17})$)')

# 匹配设置比特预警值
alert_set = re.compile(r'^((.+_(high|low))=(\d+\.?\d+?)$)')

# 远程踢人命令: 移出 @<需要被移出的人>
rp_kick = re.compile(r'^(?:移出|T|t|移除|踢出|拉黑)\s*@(.+?)(?:\u2005?\s*$)')

'''
地区群
'''
city_group = {
    "北京": "Linux中国◆北京群",
    "上海": "Linux中国◆上海群",
    "广州": "Linux中国◆广州群",
}

female_group = "Linux中国◆技术美女群"


# 下方为函数定义

# 下方为函数定义

def get_time():
    return str(time.strftime("%Y-%m-%d %H:%M:%S"))


'''
机器人消息提醒设置
'''
group_receiver = ensure_one(bot.groups().search(alert_group))
logger = get_wechat_logger(group_receiver)
logger.error(str("机器人登陆成功！" + get_time()))

'''
重启机器人
'''


def _restart():
    os.execv(sys.executable, [sys.executable] + sys.argv)


'''
定时报告进程状态
'''


def heartbeat():
    while bot.alive:
        time.sleep(3600)
        # noinspection PyBroadException
        try:
            logger.error(
                get_time() + " 机器人目前在线,共有好友 【" + str(len(bot.friends())) + "】 群 【 " + str(len(bot.groups())) + "】")
        except ResponseError as e:
            if 1100 <= e.err_code <= 1102:
                logger.critical('xiaobai offline: {}'.format(e))
                _restart()


start_new_thread(heartbeat)


def get_btshq(keyword):
    url = 'http://api.chbtc.com/data/v1/ticker?currency=' + keyword + '_cny'
    r = requests.get(url)
    # r.encoding = 'utf-8'
    # f = r.text.encode('utf-8')
    f = r.text
    print(f)
    doc = json.loads(f)
    return doc['ticker']['last']


'''
定时提醒bts行情
'''


def alert_hq():
    keyword = 'bts'
    last_str = get_btshq(keyword)
    while True:
        bts_high = config.get("config", "bts_high")
        bts_low = config.get("config", "bts_low")
        last = float(last_str)
        if last >= float(bts_high):
            logger.error('最新: {}，超过最高设定值{}'.format(last_str, bts_high))
        elif last <= float(bts_low):
            logger.error('最新: {}，超过最低设定值{}'.format(last_str, bts_low))
        time.sleep(60)
        last_str = get_btshq(keyword)


start_new_thread(alert_hq)

'''
处理发送后台查询
'''


def wxai_info_post(post_data, action):
    post_url = myconfig['site_url'] + '?g=Tbkqq&m=WxAi&a=' + action
    r = requests.post(post_url, post_data)
    r.encoding = 'utf-8'
    f = r.text.encode('utf-8')
    return f


'''
条件邀请
'''


def condition_invite(user):
    if user.sex == 2:
        female_groups = bot.groups().search(female_group)[0]
        try:
            female_groups.add_members(user, use_invitation=True)
            pass
        except:
            pass
    if (user.province in city_group.keys() or user.city in city_group.keys()):
        try:
            target_city_group = bot.groups().search(city_group[user.province])[0]
            pass
        except:
            target_city_group = bot.groups().search(city_group[user.city])[0]
            pass
        try:
            if user not in target_city_group:
                target_city_group.add_members(user, use_invitation=True)
        except:
            pass


'''
判断消息发送者是否在管理员列表
'''


def from_admin(msg):
    """
    判断 msg 中的发送用户是否为管理员
    :param msg: 
    :return: 
    """
    if not isinstance(msg, Message):
        raise TypeError('expected Message, got {}'.format(type(msg)))
    from_user = msg.member if isinstance(msg.chat, Group) else msg.sender
    if from_user.name in admin_names:
        return True
    else:
        return False


'''
处理消息文本
'''


def handle_group_msg(msg):
    if msg.type is TEXT:
        msgall = proc_at_info(msg.text)
        msgtext = msgall[1]
        match = order_id.search(msgtext)
        if match:
            orderid = match.group(1)
            post_data = {'oid': orderid, 'proxywx': msg.member.name}
            reply = wxai_info_post(post_data, 'order_json')
            reply = reply.decode('utf-8')
            print(reply)
            return reply
        else:
            search_url_pattern = re.compile(u"[a-zA-z]+://[^\s]*")
            Command_result = search_url_pattern.findall(msgtext)
            if len(Command_result) > 0:
                iid = search_iid_from_url(Command_result[0])
                print(u'[INFO] LOG-->Command_result:%s' % (str(Command_result)))
                if iid == '':

                    post_data = {'proxywx': 'pioul',
                                 'msg': Command_result[0]}
                    print(post_data)
                    reply = wxai_info_post(post_data, 'taoke_info_v1')
                    reply = '@' + msg.sender.name + ': ' + reply.decode('utf-8')
                    print(reply)
                    return reply
                else:
                    post_data = {'iid': iid, 'proxywx': 'pioul'}
                    print(post_data)
                    reply = wxai_info_post(post_data, 'taoke_info_v1')
                    reply = '@' + msg.sender.name + ': ' + reply.decode('utf-8')
                    print(reply)
                    return reply


            # elif msg.text.find('http') >= 0:
            #    post_data = {'group': msg.sender.name, 'proxywx': msg.member.name,
            #                 'msg': msg.text}
            #    reply = wxai_info_post(post_data, 'taoke_info')

            else:
                search_pattern = re.compile(u"^(买|找|帮我找|有没有|我要买|宝宝要|宝宝买|我要找)\s?(.*?)$")
                Command_result = search_pattern.findall(msgtext)

                if len(Command_result) == 1:
                    skey = Command_result[0][1]
                    post_data = {'proxywx': 'pioul', 'kw': skey}
                    return_data = wxai_info_post(post_data, 'search_items_by_key')
                    return_data = return_data.decode('utf-8')
                    if return_data != '':
                        reply = '@' + msg.member.name + u' 搜索结果：%s' % (return_data)

                        print(reply)
                        return reply
                    else:
                        return_data = u'没找到，请到网站查找!http://www.13bag.com'
                        reply = '@' + msg.member.name + u' 搜索结果：%s' % (return_data)
                        print(reply)
                        return reply
                else:
                    if tuling_switch:
                        tuling = Tuling(api_key='0c68515ebcb2920ea3844d4f8fba60fe')
                        tuling.do_reply(msg)
                    else:
                        reply = '@' + msg.member.name + ': ' + welcome_text
                        print(reply)
                        return reply


def handle_private_msg(msg):
    if msg.type is TEXT:
        search_url_pattern = re.compile(u"[a-zA-z]+://[^\s]*")
        Command_result = search_url_pattern.findall(msg.text)
        if len(Command_result) > 0:
            iid = search_iid_from_url(Command_result[0])
            print(u'[INFO] LOG-->Command_result:%s' % (str(Command_result)))
            if iid == '':

                post_data = {'proxywx': 'pioul',
                             'msg': Command_result[0]}
                print(post_data)
                reply = wxai_info_post(post_data, 'taoke_info_v1')
                reply = reply.decode('utf-8')
                print(reply)
                return reply
            else:
                post_data = {'iid': iid, 'proxywx': 'pioul'}
                print(post_data)
                reply = wxai_info_post(post_data, 'taoke_info_v1')
                reply = reply.decode('utf-8')
                print(reply)
                return reply

        else:
            search_pattern = re.compile(u"^(买|找|帮我找|有没有|我要买|宝宝要|宝宝买|我要找)\s?(.*?)$")
            Command_result = search_pattern.findall(msg.text)

            if len(Command_result) == 1:
                skey = Command_result[0][1]
                post_data = {'proxywx': 'pioul', 'kw': skey}
                return_data = wxai_info_post(post_data, 'search_items_by_key')
                return_data = return_data.decode('utf-8')
                if return_data != '':
                    reply = u' 搜索结果：%s' % (return_data)

                    print(reply)
                    return reply
                else:
                    return_data = u'没找到，请到网站查找!http://www.13bag.com'
                    reply = u' 搜索结果：%s' % (return_data)
                    print(reply)
                    return reply
            else:
                if tuling_switch:
                    tuling = Tuling(api_key='0c68515ebcb2920ea3844d4f8fba60fe')
                    tuling.do_reply(msg)
                else:
                    reply = invite_text
                    print(reply)
                    return reply


'''
查找iid,通过url
'''


def search_iid_from_url(x):
    # 从消息中提取的url来进行iid的提取，这个函数代扩容！！
    search_iid_pattern = re.compile(u"(http|https)://(item\.taobao\.com|detail\.tmall\.com)/(.*?)id=(\d*)")
    search_iid_pattern_2 = re.compile(u'(http|https)://(a\.m\.taobao\.com)/i(\d*)\.htm')
    r = requests.get(x, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36'})
    iid = ''
    temp = search_iid_pattern.findall(r.url)
    if len(temp) == 0:
        try:
            iid = search_iid_pattern.findall(r.content)[0][3]
        except:
            try:
                iid = search_iid_pattern_2.findall(r.content)[0][2]
            except:
                pass
    else:
        iid = temp[0][3]
    return iid


def proc_at_info(msg):
    if not msg:
        return '', []
    segs = msg.split(u'\u2005')
    str_msg_all = ''
    str_msg = ''
    infos = []
    if len(segs) > 1:
        for i in range(0, len(segs) - 1):
            segs[i] += u'\u2005'
            pm = re.search(u'@.*\u2005', segs[i]).group()
            if pm:
                name = pm[1:-1]
                string = segs[i].replace(pm, '')
                str_msg_all += string + '@' + name + ' '
                str_msg += string
                if string:
                    infos.append({'type': 'str', 'value': string})
                infos.append({'type': 'at', 'value': name})
            else:
                infos.append({'type': 'str', 'value': segs[i]})
                str_msg_all += segs[i]
                str_msg += segs[i]
        str_msg_all += segs[-1]
        str_msg += segs[-1]
        infos.append({'type': 'str', 'value': segs[-1]})
    else:
        infos.append({'type': 'str', 'value': segs[-1]})
        str_msg_all = msg
        str_msg = msg
    return str_msg_all.replace(u'\u2005', ''), str_msg.replace(u'\u2005', ''), infos


def get_hq_chbtc(keyword):
    url = 'http://api.chbtc.com/data/v1/ticker?currency=' + keyword + '_cny'
    r = requests.get(url)
    # r.encoding = 'utf-8'
    # f = r.text.encode('utf-8')
    f = r.text
    print(f)
    doc = json.loads(f)
    timeArray = time.localtime(int(doc['date']) / 1000)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    ret_msg = keyword + '''
最新成交价：￥{}
买一：￥{}
卖一：￥{}
最高：￥{}
最低：￥{}
成交量：{}
时间：{}
		'''
    return ret_msg.format(doc['ticker']['last'], doc['ticker']['buy'], doc['ticker']['sell'], doc['ticker']['high'],
                          doc['ticker']['low'], doc['ticker']['vol'], otherStyleTime)


def get_hq(keyword, platform):
    if platform == 'okcoin':
        apikey = '99ad2439-28f3-4297-8532-54ce8b7dc52c'
        secretkey = 'E1AE48319FF5C7C6ADA39C3040ACC6B8'
        okcoinRESTURL = 'www.okcoin.cn'  # 请求注意：国内账号需要 修改为 www.okcoin.cn
        okcoinSpot = OKCoinSpot(okcoinRESTURL, apikey, secretkey)
        ticker_key = keyword + '_cny'
        f = okcoinSpot.ticker(ticker_key)
        doc = f
        # doc = json.loads(f)
        print(u' 现货行情 ')
        print(doc)
        timeArray = time.localtime(int(doc['date']))
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        ret_msg = keyword + '''
最新成交价：￥{}
买一：￥{}
卖一：￥{}
最高：￥{}
最低：￥{}
成交量：{}
时间：{}
		'''
        return ret_msg.format(doc['ticker']['last'], doc['ticker']['buy'], doc['ticker']['sell'], doc['ticker']['high'],
                              doc['ticker']['low'], doc['ticker']['vol'], otherStyleTime)
    elif platform == 'chbtc':
        hq = get_hq_chbtc(keyword)

        print(hq)
        return hq
    else:
        pass


'''
远程踢人命令
'''


def remote_kick(msg):
    if msg.type is TEXT:
        match = rp_kick.search(msg.text)
        if match:
            name_to_kick = match.group(1)

            if not from_admin(msg):
                return '感觉有点不对劲… @{}'.format(msg.member.name)

            member_to_kick = ensure_one(list(filter(
                lambda x: x.name == name_to_kick, msg.chat)))
            if member_to_kick == bot.self:
                return '无法移出 @{}'.format(member_to_kick.name)
            if member_to_kick in admins:
                return '无法移出 @{}'.format(member_to_kick.name)

            member_to_kick.remove()
            return '成功移出 @{}'.format(member_to_kick.name)


'''
邀请消息处理
'''


def get_new_member_name(msg):
    # itchat 1.2.32 版本未格式化群中的 Note 消息
    from itchat.utils import msg_formatter
    msg_formatter(msg.raw, 'Text')

    for rp in rp_new_member_name:
        match = rp.search(msg.text)
        if match:
            return match.group(1)


'''
定义邀请用户的方法。
按关键字搜索相应的群，如果存在相应的群，就向用户发起邀请。
'''


def invite(user, keyword):
    group = bot.groups().search(keyword_of_group[keyword])
    print(len(group))
    if len(group) > 0:
        target_group = ensure_one(group)
        if user in target_group:
            content = "您已经加入了 {} [微笑]".format(target_group.nick_name)
            user.send(content)
        else:
            try:
                target_group.add_members(user, use_invitation=True)
            except:
                user.send("邀请错误！机器人邀请好友进群已达当日限制。请您明日再试")
    else:
        user.send("该群状态有误，您换个关键词试试？")


# 下方为消息处理

'''
处理加好友请求信息。
如果验证信息文本是字典的键值之一，则尝试拉群。
'''


@bot.register(msg_types=FRIENDS)
def new_friends(msg):
    user = msg.card.accept()
    if msg.text.lower() in keyword_of_group.keys():
        invite(user, msg.text.lower())
    else:
        print(user.name)
        user.send(invite_text)


@bot.register(Friend, msg_types=TEXT)
def exist_friends(msg):
    if msg.text.lower() in keyword_of_group.keys():
        invite(msg.sender, msg.text.lower())
    else:
        ret_msg = handle_private_msg(msg)
        if ret_msg:
            return ret_msg

        else:
            pass


# 管理群内的消息处理
@bot.register(Group, except_self=False)
def wxpy_group(msg):
    ret_msg = remote_kick(msg)
    if ret_msg:
        return ret_msg
    elif msg.is_at:

        ret_msg = handle_group_msg(msg)
        if ret_msg:
            return ret_msg

        else:
            pass


@bot.register(Group, CARD)
def kickgg(msg):
    ret_msg = remote_kick(msg)
    if ret_msg:
        return ret_msg
    else:
        pass


@bot.register(Group, NOTE)
def welcome(msg):
    name = get_new_member_name(msg)
    if name:
        return welcome_text.format(name)


@bot.register(groups, TEXT)
def btchq(msg):
    if msg.text.lower() in keyword_of_hqapi.keys():
        ret_msg = get_hq(msg.text.lower(), keyword_of_hqapi[msg.text.lower()])
        if ret_msg:
            return ret_msg
        else:
            pass
    else:
        match = alert_set.findall(msg.text.lower())
        if match:
            print(match)
            config.set("config", match[0][1], match[0][3])
            config.write(open("conf.ini", "w"))
            return '设置成功!'



            # orderid = match.group(1)


embed()
