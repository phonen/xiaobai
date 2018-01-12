#!/usr/bin/env python3
# coding: utf-8

from wxpy import *
import config
import re
from wxpy.utils import start_new_thread
import time
import os
import platform
from importlib import reload
import redis
'''
使用 cache 来缓存登陆信息，同时使用控制台登陆
'''
console_qr = (False if platform.system() == 'Windows' else True)
bot = Bot('bot.pkl', console_qr=console_qr)
bot.messages.max_history = 0
'''
开启 PUID 用于后续的控制
'''
bot.enable_puid('wxpy_puid.pkl')
'''
邀请信息处理
'''
rp_new_member_name = (
    re.compile(r'^"((\n?.?)+)"通过'),
    re.compile(r'邀请"((\n?.?)+)"加入'),
    re.compile(r'invited "((\n?.?)+)" to the group chat'),
)

# 远程踢人命令: 移出 @<需要被移出的人>
rp_kick = re.compile(r'^(?:移出|移除|踢出|拉黑)\s*@((\n?.?)+?)(?:\u2005?\s*$)')

# 监控群监控等级
alert_level = 30  # DEBUG: 10, INFO: 20, WARNING: 30, ERROR: 40, FATAL: 50

# 下方为函数定义


def fresh_groups():
    '''
    管理员群及被管理群初始化
    '''
    global groups, admin_group
    # 格式化被管理群 Groups
    try:
        allgroups = bot.groups(update=True)
        groups = list(
            filter(lambda x: x.name.startswith(config.group_prefix),
                   allgroups.search(config.group_prefix)))
        groups += list(
            filter(lambda x: x.name in config.additional_groups, allgroups))
    except:
        print("查找被管理群出错！请检查被管理群前缀（group_prefix）是否配置正确")
        quit()

    # 格式化管理员群 Admin_group
    try:
        admin_group = ensure_one(
            bot.groups(update=True).search(config.admin_group_name))
    except:
        print("查找管理员群出错！请检查管理群群名（admin_group_name）是否配置正确")
        print("现将默认设置为只有本帐号为管理员")
        admin_group = None


def get_time():
    return str(time.strftime("%Y-%m-%d %H:%M:%S"))


def get_logger():
    '''
    机器人消息提醒设置
    '''
    global alert_receiver, logger
    if config.alert_group:
        try:
            alert_receiver = ensure_one(bot.groups().search(
                config.alert_group))
        except:
            print("警报群设置有误，请检查群名是否存在且唯一")
            alert_receiver = bot.file_helper
    else:
        alert_receiver = bot.file_helper
    logger = get_wechat_logger(alert_receiver, level=alert_level)


def heartbeat():
    '''
    定时报告进程状态
    '''
    while bot.alive:
        time.sleep(3600)
        # noinspection PyBroadException
        try:
            logger.error(status())
        except ResponseError as e:
            if 1100 <= e.err_code <= 1102:
                logger.critical('LCBot offline: {}'.format(e))
                _restart()


def random_sleep():
    '''
    随机延时
    '''
    from random import randrange
    rnd_time = randrange(2, 7)
    time.sleep(rnd_time)


def _restart():
    '''
    重启机器人
    '''
    os.execv(sys.executable, [sys.executable] + sys.argv)


def status():
    '''
    状态汇报
    '''
    status_text = get_time() + " 机器人目前在线,共有好友 【" + str(len(
        bot.friends())) + "】 群 【" + str(len(bot.groups())) + "】"
    return status_text



fresh_groups()

get_logger()
#logger.error(str("登陆成功！" + get_time()))

#start_new_thread(heartbeat)


def fresh_bsj():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    while True:
        content = r.rpop("content1")
        if content == None:
            time.sleep(60)
        else:
            logger.error(content)
            time.sleep(60)



start_new_thread(fresh_bsj)

@bot.register(groups, except_self=False)
def sync_my_groups(msg):
    sync_message_in_groups(msg, groups)
embed()