
import logging
import threading

def create_new_thread(function_name, *args):
    """
    创建新线程
    :param function_name: 函数名称
    :param args: 函数的参数
    :return:
    """
    # 创建线程执行程序
    # 创建线程
    logging.info('当前运行的线程数为: {}'.format(len(threading.enumerate())))
    t = threading.Thread(target=function_name, args=args)
    logging.info('创建新线程执行后台程序执行函数: {}'.format(function_name.__name__))
    # 守护线程
    t.setDaemon(True)
    # 启动
    t.start()
