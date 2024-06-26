
import os
import random
import logging
from datetime import datetime

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from tkinter import messagebox

from IPCRunningTime import ipc_running_time, updata_dict_hour
from IPSRunningTime import read_errorlog
from ReadHostcfg import read_hostcfg
from ReadPassword import read_config
from SysteminfoRuningTime import get_systeminfo_return
from Threading import create_new_thread
from Logging import logging_set_fun
from KeyVariableDefinition import IPSA, IPSB, LOCAL
from KeyVariableDefinition import color_dict, window_with, errorlog_folder_path, hour_loop, warning_hour, refresh_hour


# def updata_dict_hour(equip_dict):
#     """
#     将设备字典中设备的uptime时间由datatime格式转换为小时数
#     :param equip_dict: 设备字典
#     :return:
#     """
#     if equip_dict:
#         for key, value in equip_dict.items():
#             # key 是设备名
#             # value 是设备字典 包括uptime IP install 等信息
#             try:
#                 for item in ['uptime', 'install']:
#                     if item in value:
#                         equip_dict[key][item] = datetime_to_hours(value[item])
#             except Exception as e:
#                 logging.error(f'{equip_dict} 中 {key} 转换时间出错，错误信息：{e}')




def record_time(dict_info, counter, pd):
    """
    记录、显示及判断运行时间
    :param dict_info: 设备运行时间的自动
    :param counter: 计数器 用于label_list选择对应的label对象
    :param pd: 进度条对象
    :return:
    """
    if dict_info:
        for key, value in dict_info.items():
            if value is not None and "uptime" in value:
                hours = round(value["uptime"], 2)
                text = '{0} 已运行：{1} 小时'.format(key, hours)
                # 判断时间是否超过规定时间 超过的话 需要弹出对话框
                if hours > warning_hour:
                    # 提示框会阻断程序运行 需要手动点击以后才会继续执行 这样也方便提醒用户
                    messagebox.showwarning('警告',
                                           '{0} 已运行：{1} 小时 超过建议重启时间 {2} 小时. \n 请尽快重启设备！'.format(key, hours, warning_hour))

            else:
                text = '{} ：运行时间获取失败！'.format(key)
            # 如果执行情况如何 都要返回一下内容，并更新GUI内容和进度条
            logging.info(text)
            label_dict[key].config(text=text)
            counter += 1
            if pd.winfo_exists():
                pd['value'] += 1
            main_gui.update()


    return counter


def get_all_equipment_running_time(ipc_dict):
    """
    获取所设备的运行时间字典
    :param ipc_dict: hostcfg中获取的操作机字典
    :return:
    """
    #开始执行就将 run_onetime_flag置为0 阻止其他程序再执行
    global run_onetime_flag
    run_onetime_flag = 0

    # 设置进度条
    pd = ttk.Progressbar(main_gui, length=window_with, mode='determinate', orient=tk.HORIZONTAL)
    pd['value'] = 0
    pd['maximum'] = len(ipc_dict)

    # 这里将联锁机、本机和其他工控机的获取时间分开
    counter = 0

    # 获取本机运行时间 第一个顺序 因为默认设备
    logging.info('获取本机运行时间：')
    local_time_dict = get_systeminfo_return()
    updata_dict_hour(local_time_dict)
    ipc_dict['本机'] = local_time_dict
    local_dict = dict([(key, ipc_dict[key]) for key in [LOCAL]])
    counter = record_time(local_dict, counter, pd)

    # 查询到第一个信息后 显示进度条
    pd.pack()

    # 获取联锁机运行时间
    logging.info('获取联锁机运行时间：')
    read_errorlog(ipc_dict)
    if IPSA in ipc_dict or IPSB in ipc_dict:
        ips_dict = dict([(key, ipc_dict[key]) for key in [IPSA, IPSB]])
        counter = record_time(ips_dict, counter, pd)
    else:
        logging.info('联锁机运行时间获取失败！')

    # 获取其他工控机运行时间
    other_equipment_dict = [key for key in list(ipc_dict.keys()) if key not in [IPSA, IPSB, LOCAL]]
    if len(other_equipment_dict) != 0:
        logging.info('获取其他工控机运行时间：')
        # ipc_dict传入函数 更新所有其他设备的时间
        ipc_running_time(ipc_dict, config_flag)
        # 取其他设备的字典
        other_equipment_dict = dict([(key, ipc_dict[key]) for key in other_equipment_dict])
        record_time(other_equipment_dict, counter, pd)
    else:
        logging.info('其他工控机运行时间获取失败！')

    logging.info('所有设备信息获取完毕！')

    # 取消label
    label_num = [item for item in main_gui.winfo_children() if isinstance(item, tk.Label)]
    if len(label_num) == len(ipc_dict) + 1:
        label.destroy()

    # 如果进度条存在 且已经达到最大 则消除
    if pd.winfo_exists() and pd['value'] == len(label_dict):
        pd.destroy()
        logging.info('取消进度条显示！')

    #执行完毕 run_onetime_flag置为1 使得其他程序可以继续执行
    run_onetime_flag = 1


def get_onetime():
    """
    运行一次查询时间
    :return:
    """
    if run_onetime_flag:
        # 新开一个进程 执行获取运行时间的主函数
        logging.info('*' * 20 + str(datetime.now()) + '*' * 20)
        get_all_equipment_running_time(ipc_dict)
        # 定义执行完一次的时间
        global last_research_time
        last_research_time = datetime.now()

    else:
        text = '查询仍在进行中，本次查询未进行，请稍后再试!'
        logging.info(text)
        label_num = [item for item in main_gui.winfo_children() if isinstance(item, tk.Label)]
        if len(label_num) == len(ipc_dict) + 1:
            label.config(text=text)



def run_main_loop():
    """
    周期性执行查询
    :return:
    """
    create_new_thread(get_onetime)

    main_gui.after(int(1000 * 3600 * hour_loop), run_main_loop)


def run_refresh_loop():
    """
    周期性更新界面时间显示
    :return:
    """
    try:
        if run_onetime_flag:
            # 刷新颜色主题
            theme_refresh()
            # 计算时间
            logging.info('执行一次运行时间的更新，上一次查询时间是 {}'.format(str(last_research_time)))
            # logging.info(f'上一次查询到的运行时间是： {ipc_dict}')
            # 计算当前时间与上一次执行时间的时间差
            gap = (datetime.now().timestamp() - last_research_time.timestamp()) / 3600
            # 更新ipc_dict内容
            for key, value in ipc_dict.items():
                if 'uptime' in value:
                    new_hours = value['uptime'] + gap
                    ipc_dict[key]['uptime'] = new_hours
                    hours = round(new_hours, 2)
                    text = '{0} 已运行：{1} 小时'.format(key, hours)
                    label_dict[key].config(text=text)
            main_gui.update()
            logging.info('本次更新后的运行时间是： {}'.format(ipc_dict))
        else:
            text = '查询仍在进行中，本次时间更新未进行!'
            logging.info(text)

    except Exception as e:
        logging.error('刷新时间出错，错误代码：{}'.format(e))

    main_gui.after(int(1000 * 3600 * refresh_hour), run_refresh_loop)


def theme_refresh():
    """
    主题更新，用于重新查询时更新主题及刷新时间时更新主题
    :return:
    """
    label_c = get_colour_theme()
    for i, (key, value) in enumerate(ipc_dict.items()):
        label_dict[key].config(bg=label_c[i % 5])
    main_gui.update()


def re_define_close_function():
    """
    点击关闭按钮后最小化窗口 而不是直接关闭
    :return:
    """
    logging.info('最小化窗口！')
    main_gui.iconify()


def get_colour_theme():
    """
    随机获取主题序号
    :return:
    """
    theme_len = len(color_dict)
    theme_num = random.randint(0, theme_len - 1)
    logging.info('随机选择的主题序号是：{}'.format(theme_num))
    return color_dict['theme{}'.format(theme_num)]


def help_menu():
    """
    点击说明菜单后弹出提示框
    :return:
    """
    text = ' 1.本程序每隔“{0}”小时查询一次各个设备运行时间。{1}' \
           ' 2.设备运行时间=当前时间与查询时刻的时间差+查询时刻获得的时间。{1}'\
           ' 3.在两次执行查询操作之间，可能存在运行时间与设备实际运行时间不一致的情况，' \
           '例如：在两次查询之间设备出现了重启，时间未更新，所以存在差异，{1}' \
           '可点击“{2}”更新查询信息。'.format(hour_loop, chr(13), menu_name1)

    messagebox.showinfo(menu_name3, text)


def install_hours_menu():
    """
    点击设备年限菜单后弹出提示框
    :return:
    """
    text = ''
    for key, value in ipc_dict.items():
        if 'install' in value:
            year = value["install"] / (24 * 365)
            text += ' {0} 已安装年限：{1} 年 '.format(key, round(year, 2)) + chr(13)

    messagebox.showinfo(menu_name2, text)


def refresh_menu():
    """
    点击数据刷新菜单后操作
    :return:
    """
    logging.info('点击"{}"菜单'.format(menu_name1))

    if run_onetime_flag == 0:
        # =0 代表正在执行
        # 正在执行 则显示lable
        # 先判断有没有这个label
        label_num = [item for item in main_gui.winfo_children() if isinstance(item, tk.Label)]
        if len(label_num) == len(ipc_dict):
            # ipc_dict 就是既有的设备label
            # 设置提示label
            global label
            label = tk.Label(main_gui, text='信息查询中···')
            label.pack()

    # 刷新颜色主题
    theme_refresh()
    # 重新查询
    create_new_thread(get_onetime)


if __name__ == "__main__":

    # 执行日志程序
    logging_set_fun()

    # 一次查询是否执行及是否执行完毕的flag
    # 1 执行完毕
    # 0 正在执行中
    run_onetime_flag = 1

    # 定义最后一次执行的时间，执行完一次后会更新
    last_research_time = datetime.now()

    # 定义设备字典, 用于设备布局和时间的更新
    ipc_dict = {LOCAL: {}}
    # 如果errorlog文件夹存在 则增加两个数量
    if os.path.exists(errorlog_folder_path):
        ipc_dict[IPSA] = {}
        ipc_dict[IPSB] = {}
    # 这里以hostcfg中节点为准（因为是发布文件），如果存在有些hostcfg节点没有配置密码的情况 应该把对应的ipc_dict中的key删掉
    # 获取 mmi个数并合并到设备数量中
    read_hostcfg(ipc_dict)

    main_gui = tk.Tk()
    main_gui.title('联锁设备运行时间显示')
    # main_gui.iconbitmap('')

    # 设置窗口最顶端
    main_gui.wm_attributes('-topmost', True)
    # 设置透明度0.9
    main_gui.wm_attributes('-alpha', 0.9)
    # 设置窗口为工具窗口（取消最小化 最大化 及图标显示）
    main_gui.wm_attributes('-toolwindow', True)

    # 将自定义的关闭操作绑定到关闭按钮上
    main_gui.protocol("WM_DELETE_WINDOW", re_define_close_function)

    # 窗口宽度（第一个参数）、高度都不可调节
    main_gui.resizable(False, False)
    # 获取显示器高度
    screen_height = main_gui.winfo_screenheight()
    # 设置窗口最大高度不得超过 显示器高度的 80%
    main_gui.maxsize(window_with, int(screen_height * 0.8))

    # 增加菜单
    menu_name1 = '刷新数据'
    menu_name2 = '设备年限'
    menu_name3 = '说明'

    menubar = tk.Menu(main_gui)
    menubar.add_cascade(label=menu_name1, command=refresh_menu)
    menubar.add_cascade(label=menu_name2, command=install_hours_menu)
    menubar.add_cascade(label=menu_name3, command=help_menu)
    main_gui.config(menu=menubar)

    # 字体相关属性设置
    label_c = get_colour_theme()
    label_w = 50
    label_h = 3
    label_f = tkFont.Font(root=main_gui, family='微软雅黑', size=12, weight=tkFont.BOLD)

    global label_dict, config_flag
    # 这里需要读一下config中的password内容 如果有password则显示 如果password都没有 这里就不显示了
    config_flag = read_config(ipc_dict)
    # 存放需要删除的key
    dict_del_key_list = []
    for key, value in ipc_dict.items():
        if 'password' not in value and 'IP' in value:
            # 由于联锁机和本机都没有'password'这一项 但是仍然需要保留 只有操作机是有IP这个key的
            dict_del_key_list.append(key)
    for key in dict_del_key_list:
        ipc_dict.pop(key)
        logging.info('设备字典中由于没有设置密码，需要删除key是：{}'.format(key))
    # 根据 ipc_dict 中设备名称 设置label变量
    label_dict = dict([(key, None) for key in list(ipc_dict.keys())])
    # 布局
    for i, (key, value) in enumerate(ipc_dict.items()):
        # 定义label
        exec('''label_{0} = tk.Label(main_gui,
                                    text='{1} 运行时间获取中。。。',
                                    height=label_h,
                                    width=label_w,
                                    font=label_f,
                                    anchor=tk.CENTER,
                                    bg=label_c[{0} % 5])'''.format(i, key))
        # 添加到列表
        exec('label_dict["{1}"] = label_{0}'.format(i, key))
        exec('label_{}.pack()'.format(i))



    # winfo_ismapped() 是否显示
    # winfo_exists() 是否存在
    # winfo_children() 所有子控件


    # 循环执行主程序，周期性（hour_loop）查询一次时间
    run_main_loop()
    # 刷新主界面时间显示，因为查询时间与当前时间存在时间差，通过刷新这个时间 让界面的显示也能更实时一点
    run_refresh_loop()

    main_gui.mainloop()
