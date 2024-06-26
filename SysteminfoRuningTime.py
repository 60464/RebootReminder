"""
使用systeminfo命令获取系统运行时间（小时数）
该方法适用于win7及以上版本， xp系统systeminfo中的返回内容需要格外处理（显示的是已运行时间 0天0小时0分0秒）
该方法可以实现远程访问操作机的运行时间
另外还可以获取系统的安装时间（可以通过这个时间判断工控机的寿命）

具体用法：
systeminfo [/s <computer> [/u <domain>\<username> [/p <password>]]] [/fo {TABLE | LIST | CSV}] [/nh]

systeminfo /s 10.6.3.206 /u administrator /p casco123

"""
import os
import logging
import subprocess
from datetime import datetime

from Logging import logging_set_fun



def get_cmd_return(cmd):
    """
    通过subprocess.Popen函数获取cmd命令行返回内容
    :param cmd: cmd的输入字符串
    :return: cmd返回的字符串
    """
    # 32bit python存在 无法识别cmd返回中文字符的问题 64bit python没有这个问题
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         # windows 中文的编码格式
                         # 32bit Python 没有encoding选项 通过decode('gb2312')方法来解码
                         # encoding='gb2312'
                         )
    # 输出stdout
    return p.communicate()[0].decode('gb2312')


def os_info():
    """
    获得操作系统信息记录
    :return:
    """
    os_ver = None
    try:
        os_ver_str = get_cmd_return('ver')
        if '5.1.' in os_ver_str:
            os_ver = 'WIN XP'
        if '6.1.' in os_ver_str:
            os_ver = 'WIN 7'
        if '10.' in os_ver_str:
            os_ver = 'WIN 10'
        if '6.2.' in os_ver_str:
            os_ver = 'WIN 8'
        if 'PROGRAMFILES(X86)' in os.environ:
            os_bit = '64bit系统'
        else:
            os_bit = '32bit系统'
        logging.warning('操作系统信息：{0} {1}'.format(os_ver, os_bit))
    except:
        logging.error('操作系统信息获取失败！')

    return os_ver


win_os = os_info()


def get_cmd_return_with_input_xp(cmd):
    """
    通过subprocess.Popen函数获取cmd命令行返回内容 （空密码的时候 批处理将等待回车的输入 这里是带回车输入的popen）
    :param cmd: cmd的输入字符串
    :return: cmd返回的字符串
    """
    # 32bit python存在 无法识别cmd返回中文字符的问题 64bit python没有这个问题
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         # windows 中文的编码格式
                         # encoding='gb2312'
                         )
    # 向子进程的stdin写入数据
    p.stdin.write(b'\n')
    p.stdin.close()
    # 输出stdout
    return p.communicate()[0].decode('gb2312')


def get_cmd_return_with_input(cmd):
    """
    通过subprocess.Popen函数获取cmd命令行返回内容 （空密码的时候 批处理将等待回车的输入 这里是带回车输入的popen）
    :param cmd: cmd的输入字符串
    :return: cmd返回的字符串
    """
    # 32bit python存在 无法识别cmd返回中文字符的问题 64bit python没有这个问题
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         # windows 中文的编码格式
                         encoding='gb2312'
                         )
    # 向子进程的stdin写入数据
    p.stdin.write('\n')
    p.stdin.close()
    # 输出stdout
    return p.communicate()[0]


def get_date_from_str(date_str):
    """
    将字符串形式的日志转换成datetime格式
    :param str: '     2024/1/25, 9:11:27'
    :return: datetime格式日期
    """
    # 去掉前后的空格
    date_str = date_str.strip()
    # 这里不加try-except 目的是为了让出错的情况暴露出来
    # 即便这里出错 上层函数有捕获异常的错误机制 不影响程序正常进行
    # 安装时间和运行时间都用这个函数解析
    # 对于xp系统来说 安装时间的格式是 '%Y-%m-%d, %H:%M:%S'
    # 其他系统的 安装和运行时间格式都是 '%Y/%m/%d, %H:%M:%S'
    date_format = '%Y/%m/%d, %H:%M:%S'
    if win_os == 'WIN XP':
        date_format = '%Y-%m-%d, %H:%M:%S'
    return datetime.strptime(date_str, date_format)


def get_hours_from_str_xp(date_str):
    """
    获取xp系统的运行时间
    :param date_str: 分隔后的后半部分
    :return: 已运行的小时数
    """
    # 系统启动时间:     0 天 0 小时 18 分 32 秒

    total_hours = 0
    try:
        if '天' in date_str and '小时' in date_str and '分' in date_str and '秒' in date_str:
            days, part2 = date_str.split('天')
            hours, part3 = part2.split('小时')
            mins, part4 = part3.split('分')
            secs = part4.split('秒')[0]
            total_hours = int(days.strip()) * 24 + int(hours.strip()) + int(mins.strip())/60 + int(secs.strip())/3600
        else:
            logging.error('XP操作系统获取的系统启动时间是：{}'.format(date_str))
    except Exception as e:
        logging.error('XP操作系统获取的系统启动时间解析出错！'.format(e))

    return total_hours


def get_systeminfo_return_without_password(cmd):
    """
    当密码为空的时候，通过systeminfo获取系统运行时间（需要输入回车）
    :param cmd: 批处理命令，默认是'systeminfo' 如果是操作机则需要IP和密码来组成命令行
    :return: 查询该设备的开机时间和安装时间 字典格式
    """
    dates_dict = {}
    logging.info('执行批处理命令：{}'.format(cmd))
    try:
        if win_os == 'WIN XP':
            return_string = get_cmd_return_with_input_xp(cmd)
        else:
            return_string = get_cmd_return_with_input(cmd)
        lines = return_string.split('\n')
        uptime_keyword = '系统启动时间:'
        install_keyword = '初始安装日期:'
        for line in lines:
            if uptime_keyword in line:
                line_part2 = line[line.find(uptime_keyword) + 7:]
                # 这里判断 xp 不一样
                if win_os == 'WIN XP':
                    # 这里获得的就是运行时间
                    date_time = get_hours_from_str_xp(line_part2)
                else:
                    # 这里获取的时间是datetime格式
                    date_time = get_date_from_str(line_part2)
                dates_dict['uptime'] = date_time
            if install_keyword in line:
                line_part2 = line[line.find(install_keyword) + 7:]
                date_time = get_date_from_str(line_part2)
                dates_dict['install'] = date_time
        if len(dates_dict) == 0:
            # 当获取失败的时候 看看返回信息是啥
            logging.warning('systeminfo获取失败！返回信息：{}'.format(return_string))
    except Exception as e:
        logging.error('systeminfo获取出错！错误信息：{}'.format(e))

    return dates_dict


def get_systeminfo_return(cmd='systeminfo'):
    """
    通过systeminfo获取系统运行时间
    :param cmd: 批处理命令，默认是'systeminfo' 如果是操作机则需要IP和密码来组成命令行
    :return: 查询该设备的开机时间和安装时间 字典格式
    """
    dates_dict = {}
    logging.info('执行批处理命令：{}'.format(cmd))
    try:
        return_string = get_cmd_return(cmd)
        # logging.debug(return_string)
        lines = return_string.split('\n')
        uptime_keyword = '系统启动时间:'
        install_keyword = '初始安装日期:'
        for line in lines:
            if uptime_keyword in line:
                line_part2 = line[line.find(uptime_keyword) + 7:]
                # 这里判断 xp 不一样
                if win_os == 'WIN XP':
                    # 这里获得的就是运行时间
                    date_time = get_hours_from_str_xp(line_part2)
                else:
                    # 这里获取的时间是datetime格式
                    date_time = get_date_from_str(line_part2)
                dates_dict['uptime'] = date_time
            if install_keyword in line:
                line_part2 = line[line.find(install_keyword) + 7:]
                date_time = get_date_from_str(line_part2)
                dates_dict['install'] = date_time
        if len(dates_dict) == 0:
            # 当获取失败的时候 看看返回信息是啥
            logging.warning('systeminfo获取失败！返回信息：{}'.format(return_string))
    except Exception as e:
        logging.error('systeminfo获取出错！错误信息：{}'.format(e))

    return dates_dict


if __name__ == "__main__":
    # 函数执行的时候需要先设置日志服务的配置
    logging_set_fun()
    print(get_systeminfo_return())

