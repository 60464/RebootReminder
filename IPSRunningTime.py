"""
通过读取errorlog查询联锁机最新的运行时间

1 从哪个errorlog文件里面查
方案1：通过当前时间获取当天errorlog文件名称，并查询。
这个问题是如果查询时间比较早，比如零点或者1点查询 可能查询不到内容，这个时候查询可以查询上一天的日志，还是比较受限于查询时间
方案2：选择errorlog文件夹中文件的修改时间最新的两个文件进行查询
方案2好一点

2 查询内容
（1）只查询如下关键字
联锁B机已连续运行6449小时, DVCOM运行5158小时54分钟
联锁A机已连续运行6449小时, DVCOM运行5158小时52分钟
（2）从最后一行往前查询 减少查询次数
"""

import os
import re
import time
import logging
from datetime import datetime

from KeyVariableDefinition import errorlog_folder_path
from Logging import logging_set_fun


def get_latest_modified_files(path):
    """
    获得path路径下最新修改的2个文件绝对路径
    :param path: 文件夹地址
    :return: 两个绝对路径 如果执行错误 或者没有文件 则返回None
    """
    try:
        # 查看路径下的文件及文件修改时间
        all_file_name_path = {}
        for cur_dir, dirs, files in os.walk(path):
            for file_name in files:
                if 'ErrorLog' in file_name:
                    file_name_path = os.path.join(cur_dir, file_name)
                    file_name_path_time = os.path.getmtime(file_name_path)
                    if file_name_path not in all_file_name_path:
                        all_file_name_path[file_name_path] = file_name_path_time

        if all_file_name_path:
            # 按照修改时间对字典进行降序排序
            all_file_name_path_sorted = sorted(all_file_name_path.items(), key=lambda x: x[1], reverse=True)
            files = [i[0] for i in all_file_name_path_sorted[:2]]
            logging.info('{0} 下获取到最新修改的两个文件是：{1}'.format(path, files))
            return files
        else:
            logging.warning('{} 下未获取到errorlog文件信息！'.format(path))

    except Exception as e:
        logging.error('获取最新修改的两个文件失败！错误信息：{}'.format(e))


def get_1row_time(date, time):
    """
    完成一行时间的转换
    :param date: errorlog这一行经过split分解过的日期
    :param time: errorlog这一行经过split分解过的时间
    :return: datetime格式的时间
    """
    # 对于 date time的字符串类型 需要先判断一下
    if len(date.split('-')) == 3:
        if len(time.split(':')) == 3:
            date_time_str = date + ' ' + time
        else:
            date_time_str = date + ' ' + '00:00:00'
        # 时间转换为时间格式
        date_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    else:
        date_time = datetime.now()
        logging.warning('日期：{0} 获取异常！用当前时间替代：{1}'.format(date, date_time))

    return date_time


def get_ips_running_time(one_line):
    """
    获取联锁机连续运行时间
    :param one_line: errorlog一行的内容
    :return: errorlog一行内容中的时间（datetime格式） vle运行时间 dvcom运行时间
    """
    line_split = one_line.split()
    date_time = get_1row_time(line_split[0], line_split[1])
    # 通过re库，分隔字符串中数字，确定vle运行时间
    vle_running_time = int(re.findall('[0-9]+', line_split[2])[0])
    # 定义默认dvcom运行的时间
    dvcom_running_time = 0
    # 判断一下是否存在dvcom
    if 'DVCOM' in one_line:
        dvcom_running_time_list = re.findall('[0-9]+', line_split[3])
        dvcom_running_time = float(dvcom_running_time_list[0]) + round(float(dvcom_running_time_list[1]) / 60, 2)

    return date_time, vle_running_time, dvcom_running_time


def read_errorlog(ips_dict):
    """
    获取errorlog中联锁机运行时间
    :param ips_dict: 各个设备的字典
    :return:
    """

    ipsa_running_hours, ipsb_running_hours = 0, 0
    errorlog_files = get_latest_modified_files(errorlog_folder_path)
    if errorlog_files is not None:
        for file_address in errorlog_files:
            if os.path.isfile(file_address):
                try:
                    with open(file_address, encoding='gbk', errors="ignore") as f:
                        # 这里需要对文件大小进行查看并判断 太大的文件应该处理一下
                        # filesize = os.path.getsize(inputfile)
                        # blocksize = 1024
                        # if filesize > blocksize:
                        #     maxseekpoint = (filesize // blocksize)
                        #     f.seek((maxseekpoint - 1) * blocksize)
                        # elif filesize:
                        #     f.seek(0, 0)
                        lines = f.readlines()
                        for i in range(len(lines)-1, -1, -1):
                            try:
                                line = lines[i]
                                if len(line) > 1 and line[:2] == '20':
                                    if '联锁A机已连续运行' in line:
                                        date_time, vle_running_time, dvcom_running_time = get_ips_running_time(line)
                                        now_time = datetime.now()
                                        # 获取当前时间与记录时间的差别 从而计算当前时间系统运行的时间
                                        gap_hour = (now_time.timestamp() - date_time.timestamp()) / 3600
                                        ipsa_running_hours = vle_running_time + gap_hour
                                    if '联锁B机已连续运行' in line:
                                        date_time, vle_running_time, dvcom_running_time = get_ips_running_time(line)
                                        now_time = datetime.now()
                                        # 获取当前时间与记录时间的差别 从而计算当前时间系统运行的时间
                                        gap_hour = (now_time.timestamp() - date_time.timestamp()) / 3600
                                        ipsb_running_hours = vle_running_time + gap_hour
                                    if ipsa_running_hours != 0 and ipsb_running_hours != 0:
                                        ips_dict['联锁A机']['uptime'] = ipsa_running_hours
                                        ips_dict['联锁B机']['uptime'] = ipsb_running_hours
                                        logging.info('{0} 中 读取到联锁机运行时间：{1}'.format(file_address, ips_dict))
                                        # 读取到时间后 直接返回
                                        return
                            except Exception as e:
                                logging.error('{0} 中 {1} 行读取出错！错误信息：{2}'.format(file_address, i, e))
                                continue
                except PermissionError:
                    logging.error('{} 文件被打开！等待1s后自动重试！'.format(file_address))
                    time.sleep(1)
            else:
                logging.error('{} 文件不存在！'.format(file_address))



if __name__ == "__main__":
    logging_set_fun()
    print(read_errorlog())
