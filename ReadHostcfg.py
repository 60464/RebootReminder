"""
hostcfg配置文件读取
"""


import os
import logging
from configparser import ConfigParser

from KeyVariableDefinition import hostcfg_path
from Logging import logging_set_fun


def read_hostcfg_file(config_file_name, ipc_dict):
    """
    读取hostcfg中工控机的IP地址
    :param config_file_name: hostcfg的路径
    :return: 更新ipc_dict内容
    """
    cfg = ConfigParser()
    cfg.read(config_file_name, encoding='gbk')
    node_num = int(cfg.items('HostNum')[0][1])
    for i in range(node_num):
        ip_list = []
        node_name, node_type = '', ''
        # 循环执行node中每个变量
        for name, value in cfg.items('Host{}'.format(i + 1)):
            if name == 'name':
                node_name = value
            if name in ['ipaddr1', 'ipaddr2']:
                ip_list.append(value)
            if name == 'hosttype':
                node_type = value
        if node_type in ['MMI']:
            if node_name not in ipc_dict:
                ipc_dict[node_name] = {'IP': ip_list}


def read_hostcfg(ipc_dict):
    """
    读取hostcfg中操作机的IP地址
    :param ipc_dict:
    :return:
    """
    if os.path.isfile(hostcfg_path):
        try:
            read_hostcfg_file(hostcfg_path, ipc_dict)
            logging.info('{} 文件读取完成！'.format(hostcfg_path))
            logging.info(ipc_dict)
            return True
        except Exception as e:
            logging.error('{0} 文件读取失败！错误信息：{1}'.format(hostcfg_path, e))
            return False
    else:
        logging.warning('{} 没有找到文件！'.format(hostcfg_path))
        return False


if __name__ == "__main__":
    logging_set_fun()
    ipc_dict = {}
    read_hostcfg(ipc_dict)
    print(ipc_dict)
