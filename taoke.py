#!/usr/bin/env python3
# coding: utf-8
import re
import requests
robot_name = 'taotehui04d'

myconfig = {'site_url':'http://taotehui.co/'}
tuling_switch = False

admin_names = (
    u'山谷西西家',
)

'''
定义需要管理的群
群的PUID 可以通过 执行 export_puid.py 生成 data 文件，在data 文件中获取
'''
group_names = (
    u'淘特惠代理群NO.101',
 )

# 新人入群的欢迎语
welcome_text1 = '''🎉 欢迎 @{} 的加入！
 '''

welcome_text = '''😃 我是你的机器人好友，需要找优惠产品请@我，输入：找XXX;就会得到你想要的优惠券产品！
 我是你的机器人好友，发送要买的淘宝产品链接请@我，我会帮你找优惠券发给你哦！
 '''

invite_text = """😃 我是你的机器人好友，输入：找XXX;就会得到你想要的天猫优惠券产品！
 我是你的机器人好友，发送要买的淘宝产品链接给我，我会帮你找出产品优惠券发给你哦！
 """

keyword_of_group = {
    "测试":"机器人测试群"
}

#查询订单：*1234567890
order_id = re.compile(r'^(?:\*(\d{16,17})$)')
#设置代理编号
proxyno = re.compile(r'^(?:taotehui|buyi|yhg)\d{3,4}$')

'''
地区群
'''
city_group = {
    "测试":"机器人测试群"
}

female_group="机器人测试群"

alert_group="淘特惠技术部"

turing_key='0c68515ebcb2920ea3844d4f8fba60fe'


'''
定义函数
'''


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
判断消息发送者是否是该群的管理员
'''


def isproxy(group, proxywx):
    post_data = {'proxywx': proxywx, 'group': group}
    print(post_data)
    post_url = myconfig['site_url'] + '?g=Tbkqq&m=WxAi&a=isproxy'
    r = requests.post(post_url, post_data)
    r.encoding = 'utf-8'
    f = r.text.encode('utf-8')
    return f

def save_proxy(proxywx, msg):
		post_data = {'proxywx': proxywx, 'msg': msg}
		post_url = myconfig['site_url'] + '?g=Tbkqq&m=Ai&a=save_link'
		r = requests.post(post_url, post_data)
		r.encoding = 'utf-8'
		f = r.text.encode('utf-8')
		return f




'''
处理消息文本
'''
def handle_group_msg(msg):
    if msg.type is TEXT:
        msgall = proc_at_info(msg.text)
        msgtext = msgall[1]
        match = order_id.search(msgtext)
        match1 = proxyno.search(msgtext)
        if match:
            orderid = match.group(1)
            post_data = {'oid': orderid, 'proxywx': msg.member.name}
            reply = wxai_info_post(post_data, 'order_json')
            reply = reply.decode('utf-8')
            print(reply)
            return reply
        elif match1:
        		reply = save_proxy(msg.member.name,msgtext)
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

                    post_data = {'group': msg.sender.name, 'proxywx': msg.member.name,
                                 'msg': Command_result[0]}
                    print(post_data)
                    reply = wxai_info_post(post_data, 'taoke_info')
                    reply = reply.decode('utf-8')
                    print(reply)
                    return reply
                else:
                    post_data = {'iid': iid, 'group': msg.sender.name, 'proxywx': msg.member.name}
                    print(post_data)
                    reply = wxai_info_post(post_data, 'get_taoke_by_iid')
                    reply = reply.decode('utf-8')
                    print(reply)
                    return reply


            #elif msg.text.find('http') >= 0:
            #    post_data = {'group': msg.sender.name, 'proxywx': msg.member.name,
            #                 'msg': msg.text}
            #    reply = wxai_info_post(post_data, 'taoke_info')

            else:
                search_pattern = re.compile(u"^(买|找|帮我找|有没有|我要买|宝宝要|宝宝买|我要找)\s?(.*?)$")
                Command_result = search_pattern.findall(msgtext)

                if len(Command_result) == 1:
                    skey = Command_result[0][1]
                    post_data = {'group': msg.sender.name, 'proxywx': msg.member.name, 'kw': skey}
                    return_data = wxai_info_post(post_data, 'search_items_by_key')
                    return_data = return_data.decode('utf-8')
                    if return_data != '':
                        reply = '@' + msg.member.name + u' 搜索结果：%s' % (return_data)

                        print(reply)
                        return reply
                    else:
                        return_data = u'没找到，请到网站查找!http://www.taotehui.co'
                        reply = '@' + msg.member.name + u' 搜索结果：%s' % (return_data)
                        print(reply)
                        return reply
                else:
                    if tuling_switch:
                        tuling = Tuling(api_key=turing_key)
                        tuling.do_reply(msg)
                    else:
                        reply = '@ ' + msg.member.name + ': ' + welcome_text
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
