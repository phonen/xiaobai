#!/usr/bin/env python3
# coding: utf-8

from wxpy import *
import re
import requests
import json

'''
使用 cache 来缓存登陆信息，同时使用控制台登陆
'''
bot = Bot('bot.pkl', console_qr=False)


'''
开启 PUID 用于后续的控制
'''
bot.enable_puid('wxpy_puid.pkl')

myconfig = {'site_url':'http://taotehui.co/'}
tuling_switch = True
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
admin_puids = (
    '7c621778',
    '15518bbd'
)

'''
定义需要管理的群
群的PUID 可以通过 执行 export_puid.py 生成 data 文件，在data 文件中获取
'''
group_puids = (
    'a20c71fe',
    '43406711'
 )

# 格式化 Group
groups = list(map(lambda x: bot.groups().search(puid=x)[0], group_puids))
# 格式化 Admin
admins = list(map(lambda x: bot.friends().search(puid=x)[0], admin_puids))

# 新人入群的欢迎语
welcome_text = '''🎉 欢迎 @{} 的加入！
😃 有问题请私聊我。
'''

invite_text = """欢迎您，我是淘特惠微信群助手。
"""

'''
设置群组关键词和对应群名
* 关键词必须为小写，查询时会做相应的小写处理
'''
keyword_of_group = {
    "lfs":"Linux中国◆LFS群",
    "dba":"Linux中国◆DBA群"
}

#查询订单：*1234567890
order_id = re.compile(r'^(?:\*(\d{16,17})$)')

# 远程踢人命令: 移出 @<需要被移出的人>
rp_kick = re.compile(r'^(?:移出|T|t|移除|踢出|拉黑)\s*@(.+?)(?:\u2005?\s*$)')

'''
地区群
'''
city_group = {
    "北京":"Linux中国◆北京群",
    "上海":"Linux中国◆上海群",
    "广州":"Linux中国◆广州群",
}

female_group="Linux中国◆技术美女群"

# 下方为函数定义
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
    print(admins)
    if from_user in admins:
        return True
    else:
        if isproxy(msg.sender.name,from_user.name) == "ok":
            return True
        else:
            return False



'''
判断消息发送者是否是该群的管理员
'''


def isproxy(group, proxywx):
    post_data = {'proxywx': proxywx, 'group': group}
    post_url = myconfig['site_url'] + '?g=Tbkqq&m=WxAi&a=isproxy'
    r = requests.post(post_url, post_data)
    r.encoding = 'utf-8'
    f = r.text.encode('utf-8')
    return f

'''
处理消息文本
'''
def handle_group_msg(msg):
    if msg.type is TEXT:
        match = order_id.search(msg.text)
        if match:
            orderid = match.group(1)
            post_data = {'oid': orderid, 'proxywx': msg.member.name}
            reply = wxai_info_post(post_data, 'order_json')
            return reply
        else:
            search_url_pattern = re.compile(u"[a-zA-z]+://[^\s]*")
            Command_result = search_url_pattern.findall(msg.text)
            if len(Command_result) > 0:
                iid = search_iid_from_url(Command_result[0])
                print(u'[INFO] LOG-->Command_result:%s' % (str(Command_result)))
                if iid == '':

                    post_data = {'group': msg.sender.name, 'proxywx': msg.member.name,
                                 'msg': Command_result[0]}
                    reply = wxai_info_post(post_data, 'taoke_info')
                else:
                    post_data = {'iid': iid, 'group': msg.sender.name, 'proxywx': msg.member.name}
                    reply = wxai_info_post(post_data, 'get_taoke_by_iid')

            #elif msg.text.find('http') >= 0:
            #    post_data = {'group': msg.sender.name, 'proxywx': msg.member.name,
            #                 'msg': msg.text}
            #    reply = wxai_info_post(post_data, 'taoke_info')

            else:
                search_pattern = re.compile(u"^(买|找|帮我找|有没有|我要买|宝宝要|宝宝买|我要找)\s?(.*?)$")
                Command_result = search_pattern.findall(msg.text)

                if len(Command_result) == 1:
                    skey = Command_result[0][1]
                    post_data = {'group': msg.sender.name, 'proxywx': msg.member.name, 'kw': skey}
                    return_data = wxai_info_post(post_data, 'search_items_by_key')
                    if return_data != '':
                        reply = '@' + msg.member.name + u' 搜索结果：%s' % (return_data)
                    else:
                        return_data = u'没找到，请到网站查找!http://www.taotehui.co'
                        reply = '@' + msg.member.name + u' 搜索结果：%s' % (return_data)
                else:
                    if tuling_switch:
                        tuling = Tuling(api_key='0c68515ebcb2920ea3844d4f8fba60fe')
                        tuling.do_reply(msg)
                    else:
                        reply = '@ ' + msg.member.name + ': ' + u"对不起，工作中，不聊天，,,Ծ‸Ծ,,"


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
            if member_to_kick  == bot.self:
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
        return invite_text

@bot.register(Friend, msg_types=TEXT)
def exist_friends(msg):
    if msg.text.lower() in keyword_of_group.keys():
        invite(msg.sender, msg.text.lower())
    else:
        return invite_text


# 管理群内的消息处理
@bot.register(Group, except_self=False)
def wxpy_group(msg):
    ret_msg = remote_kick(msg)
    if ret_msg:
        return ret_msg
    elif msg.is_at:
        #return msg.text
        ret_msg = handle_group_msg(msg)
        if ret_msg:
            return ret_msg

        else:
            pass

'''
@bot.register(groups, NOTE)
def welcome(msg):
    name = get_new_member_name(msg)
    if name:
        return welcome_text.format(name)
'''



embed()
