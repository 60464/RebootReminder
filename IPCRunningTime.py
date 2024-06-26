"""
获得所有工控机设备的运行时间
"""

import logging
from datetime import datetime

from SysteminfoRuningTime import get_systeminfo_return, get_systeminfo_return_without_password
from KeyVariableDefinition import IPSA, IPSB, LOCAL

from Logging import logging_set_fun

# 测试函数 test_IPCRunningTime.py - > test_datetime_to_hours
def datetime_to_hours(date_time):
    """
    计算datetime格式时间与当前时间的小时差（设备运行时间）
    如果是datetime格式就计算 如果不是则返回传入的值
    :param date_time: 设备启动的时间 datetime格式
    :return: 小时数
    """
    if isinstance(date_time, datetime):
        date_now = datetime.now()
        hours = (date_now.timestamp() - date_time.timestamp()) / 3600
        if hours < 0:
            hours = 0
            logging.warning('函数传入时间 {0} 比当时的时间 {1} 晚，导致时间差为: {2} 小时'.format(date_time, date_now, hours))
        return hours
    else:
        return date_time


# 测试函数 test_IPCRunningTime.py - > test_updata_dict_hour
def updata_dict_hour(date_dict):
    """
    将设备字典中设备的uptime时间由datatime格式转换为小时数
    :param date_dict: 时间字典，有两个key： 'uptime', 'install'
    :return:
    """
    if date_dict:
        for key, value in date_dict.items():
            try:
                date_dict[key] = datetime_to_hours(value)
            except Exception as e:
                logging.error('{0} 中 {1} 转换时间出错，错误信息：{2}'.format(date_dict, key, e))



def ipc_running_time(ipc_dict, config_flag):
    """
    获取工控机运行时间
    :param ipc_dict: 设备信息字典
    :return:
    """

    # setp1: 根据hostcfg获取IP地址及设备名称
    # if read_hostcfg(ipc_dict):
    # setp2: 根据config获取工控机密码
    if config_flag:
        # 执行工控机的运行时间程序
        for key, value in ipc_dict.items():
            try:
                if key not in [IPSA, IPSB, LOCAL]:
                    if 'IP' in value and 'password' in value:
                        ip_list = value['IP']
                        password = value['password']
                        for ip in ip_list:
                            # 先判断网络通不通
                            # ipc_info_dict = create_new_thread(get_systeminfo_return,
                            #                                   f'systeminfo /s {ip} /u Administrator /p {password}')
                            cmd = 'systeminfo /s {0} /u Administrator /p {1}'.format(ip, password)
                            if password != '':
                                ipc_info_dict = get_systeminfo_return(cmd)
                                updata_dict_hour(ipc_info_dict)
                            else:
                                logging.warning('{} 设备密码为空！程序将输入回车后继续执行！'.format(key))
                                ipc_info_dict = get_systeminfo_return_without_password(cmd)
                                updata_dict_hour(ipc_info_dict)

                            if ipc_info_dict:
                                if 'uptime' in ipc_info_dict:
                                    # 通的话就把key的运行时间增加到字典中
                                    ipc_dict[key]['uptime'] = ipc_info_dict['uptime']
                                if 'install' in ipc_info_dict:
                                    # 通的话就把key的运行时间增加到字典中
                                    ipc_dict[key]['install'] = ipc_info_dict['install']
                                # 只要字典不为空 就说明这个IP地址是通的
                                break
                        logging.info('{0} 读取到的时间为：{1}'.format(key, ipc_info_dict))
                    else:
                        logging.warning('{} 未读取到IP地址或者密码！'.format(key))
            except Exception as e:
                logging.error('{0} 读取的时间时出错！ 错误信息：{1}'.format(key, e))
                continue



if __name__ == "__main__":
    logging_set_fun()
    print(ipc_running_time())
