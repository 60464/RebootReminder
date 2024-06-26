"""
关键的一些变量的声明
"""

# 字典中一些关键字定义
IPSA = '联锁A机'
IPSB = '联锁B机'
LOCAL = '本机'

log_file_name = 'reboot_reminder_log.txt'
hostcfg_path = r'E:\iLOCKSDM\main\HostCfg.ini'
errorlog_folder_path = r'E:\iLOCKSDM\main\log\Errorlog'
config_file = 'config.ini'
# 查询功能多少个小时执行一次
hour_loop = 12
# 运行多久进行提示
warning_hour = 24 * 365
# 界面多长时间刷新一次
refresh_hour = 1

# 1=测试模式 0=正式模式
test_flag = 1

# tk 相关变量定义
# 颜色
color_dict = {
    'theme0': ['#d2f1dc', '#98c39a', '#516850', '#879d95', '#f0c8b4'],
    'theme1': ['#e3e5de', '#6b8f78', '#828fa2', '#9dc2de', '#badbe9'],
    'theme2': ['#f4f2ec', '#f3ddc3', '#f2d58c', '#f2c54e', '#c4a27f'],
    'theme3': ['#f7f3e8', '#f2d3bf', '#f39a8f', '#d95475', '#bbb1b1'],
    'theme4': ['#f8e5c2', '#f2c69c', '#9eacb4', '#5c6c6c', '#bad077'],
    'theme5': ['#ddeff6', '#a8d8e2', '#5b7288', '#c5b8bf', '#e7dfe2'],
    'theme6': ['#eae0e9', '#e0c7e3', '#ae98b6', '#846e89', '#c6d182'],
    'theme7': ['#dfeeea', '#ebe4d0', '#e1c9a5', '#d7af83', '#9d8063']
}

# 定义GUI窗口宽度
window_with = 400

# 检查RGB这些数值是否正确
# def check_color_dict(color_dict):
#     def hex_2_digit(hex_str):
#         hex_str = hex_str[1:]
#         hex_str_list = [hex_str[:2], hex_str[2:4], hex_str[4:]]
#         for one in hex_str_list:
#             if int(one, 16) > 255:
#                 print(one)
#                 return False
#         return True
#     for key, value in color_dict.items():
#         for one in value:
#             if hex_2_digit(one) is False:
#                 print(key, one)
#                 break
#         print(key, '执行完毕 全部正确')



if test_flag:
    from configparser import ConfigParser
    cfg = ConfigParser()
    cfg.read(config_file, encoding='gbk')
    if 'PATH' in cfg.sections():
        for name, value in cfg.items('PATH'):
            if name == 'HOSTCFG'.lower():
                hostcfg_path = value
            if name == 'ERRORLOG'.lower():
                errorlog_folder_path = value
            if name == 'HOURS'.lower():
                hour_loop = float(value)
                if hour_loop > 24:
                    hour_loop = 24
                if hour_loop < 1:
                    hour_loop = 1
            if name == 'WARNING_HOURS'.lower():
                warning_hour = float(value)
            if name == 'refresh_hour'.lower():
                refresh_hour = float(value)
