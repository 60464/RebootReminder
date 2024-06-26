"""
保存密码的配置文件读取
"""


import os
import logging
from configparser import ConfigParser

from KeyVariableDefinition import config_file
from Logging import logging_set_fun


def read_config_file(config_file_name, ipc_dict):
    """
    读取config.ini中的密码
    :param config_file_name: config.ini的路径
    :return: 更新ipc_dict内容
    """
    cfg = ConfigParser()
    cfg.read(config_file_name, encoding='gbk')
    if 'PASSWORD' in cfg.sections():
        for index, name_psw in cfg.items('PASSWORD'):
            ipc_name, psw = name_psw.replace('，', ',').split(',')
            ipc_name = ipc_name.strip()
            psw = psw.strip()
            if psw == '空':
                psw = ''
            if ipc_name in ipc_dict:
                ipc_dict[ipc_name]['password'] = psw
            else:
                logging.warning('{0} 中的 {1} 在hostcfg中没有找到！'.format(config_file_name, ipc_name))
    else:
        logging.warning('{0} 配置文件中没有找到PASSWORD内容！'.format(config_file_name))


def read_config(ipc_dict):
    """
    读取config配置文件中操作机的密码
    :param ipc_dict:
    :return:
    """
    if os.path.isfile(config_file):
        try:
            read_config_file(config_file, ipc_dict)
            logging.info('{} 文件读取完成！'.format(config_file))
            return True
        except Exception as e:
            logging.error('{0} 文件读取失败！错误信息：{1}'.format(config_file, e))
            return False
    else:
        logging.warning('{} 没有找到文件！'.format(config_file))
        return False


if __name__ == "__main__":
    logging_set_fun()
    ipc_dict = {'操作A机': {}, '操作B机': {}}
    read_config(ipc_dict)
    print(ipc_dict)
