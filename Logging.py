"""
日志文件的记录
"""

import logging
from logging.handlers import RotatingFileHandler

from KeyVariableDefinition import log_file_name


def logging_set_fun():
    """
    日志服务初始设备
    :return:
    """

    logger = logging.getLogger()
    fh = logging.FileHandler(log_file_name, encoding="gbk", mode="a")
    # 创建日志记录的格式
    fmt = '%(asctime)s , %(levelname)s , %(message)s , %(filename)s-%(lineno)d , %(funcName)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(fmt, datefmt)
    # 为创建的日志记录器设置日志记录格式
    fh.setFormatter(formatter)
    # 为全局的日志工具对象添加日志记录器
    logger.addHandler(fh)
    # 创建日志的记录等级
    # logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)


if __name__ == "__main__":
    # 函数执行的时候需要先设置日志服务的配置
    logging_set_fun()
    logging.info('info message')
    logging.warning('warn message')
    logging.error('error message')
    logging.critical('critical message')
