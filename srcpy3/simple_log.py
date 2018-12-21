# -*- coding=utf-8 -*-
"""
 @file easylog.py
 @author hexueyuan(hexueyuan@qq.com)
 @date 2018/07/07
 @brief: this is a logger module, base on logging module and you can use it easyly
"""
import os
import logging
import logging.handlers
import sys

class SimpleLogger(object):
    """
    SimpleLogger support debug, trace, notice, warning, fatal
    NOTSET < DEBUG < TRACE < INFO < NOTICE < WARNING=WARN < ERROR < CRITICAL < FATAL
    """
    TRANCE_LEVEL = 15
    NOTICE_LEVEL = 25
    FATAL_LEVEL = 55

    logging.addLevelName(TRANCE_LEVEL, "TRACE")
    logging.addLevelName(NOTICE_LEVEL, "NOTICE")
    logging.addLevelName(FATAL_LEVEL, "FATAL")

    _initialized = False
    _logger = None

    def __init__(self):
        if not SimpleLogger._initialized:
            self.init()
    
    @staticmethod
    def init(log_path=None, mod_name="DEFAULT-LOG", level=logging.DEBUG,
            format="%(levelname)s: %(asctime)s :%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"):
        """
        init_log - initialize log module
    
        Args:
          log_path      - Log file path prefix.
                          Log data will go to two files: log_path.log and log_path.log.wf
                          Any non-exist parent directories will be created automatically
          level         - msg above the level will be displayed
                          DEBUG < INFO < WARNING < ERROR < CRITICAL
                          the default value is logging.INFO
          format        - format of the log
                          default format:
                          %(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s
                          INFO: 12-09 18:02:42: log.py:40 * 139814749787872 HELLO WORLD
        Raises:
            OSError: fail to create log directories
            IOError: fail to open log file
        """
        formatter = logging.Formatter(format, datefmt)
        SimpleLogger._logger = logging.getLogger(mod_name)
        SimpleLogger._logger.handlers = []
        SimpleLogger._logger.setLevel(level)

        if log_path is None:
            log_file = "/dev/stdout"
            wf_log_file = "/dev/stderr"
        else:
            log_file = log_path + ".log"
            wf_log_file = log_path + ".log.wf"
            dir = os.path.dirname(log_path)
            if not os.path.isdir(dir):
                os.makedirs(dir)

        normal_handle = logging.handlers.WatchedFileHandler(log_file)
    
        normal_handle.setLevel(level)
        normal_handle.setFormatter(formatter)
        SimpleLogger._logger.addHandler(normal_handle)
    
        wf_handle = logging.handlers.WatchedFileHandler(wf_log_file)
        wf_handle.setLevel(logging.WARNING)
        wf_handle.setFormatter(formatter)
        SimpleLogger._logger.addHandler(wf_handle)
        SimpleLogger._initialized = True

    @staticmethod
    def logger():
        """init once
        """
        if not SimpleLogger._initialized:
            SimpleLogger.init()
        return SimpleLogger._logger


def init(log_path=None, mod_name="DEFAULT-LOG", level='DEBUG',
            format="%(levelname)s: %(asctime)s :%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"):
    """global init
    """
    if level == 'ERROR':
        lev = logging.ERROR
    elif level == 'WARNING':
        lev = logging.WARNING
    elif level == 'INFO':
        lev = logging.INFO
    elif level == 'NOTICE':
        lev = SimpleLogger.NOTICE_LEVEL
    else:
        lev = logging.DEBUG
    SimpleLogger.init(log_path, mod_name, lev, format, datefmt)


def debug(message):
    """debug log
    """
    filename, line_no, fucname = __get_frame_info()
    message = __get_message(filename, line_no, fucname, message)
    SimpleLogger.logger().log(logging.DEBUG, message)


def trace(message):
    """trace log
    """
    filename, line_no, fucname = __get_frame_info()
    message = __get_message(filename, line_no, fucname, message)
    SimpleLogger.logger().log(SimpleLogger.TRANCE_LEVEL, message)


def notice(message):
    """notice log
    """
    filename, line_no, fucname = __get_frame_info()
    message = __get_message(filename, line_no, fucname, message)
    SimpleLogger.logger().log(SimpleLogger.NOTICE_LEVEL, message)


def warning(message):
    """warning log
    """
    filename, line_no, fucname = __get_frame_info()
    message = __get_message(filename, line_no, fucname, message)
    SimpleLogger.logger().log(logging.WARNING, message)


def fatal(message):
    """fatal log
    """
    filename, line_no, fucname = __get_frame_info()
    message = __get_message(filename, line_no, fucname, message)
    SimpleLogger.logger().log(SimpleLogger.FATAL_LEVEL, message)


def __get_message(filename, line_no, fucname, message):
    message = "[%s:%d %s] %s" % (filename, line_no, fucname, message)
    return message


def __get_frame_info():
    frame = sys._getframe(2)
    line_no = frame.f_lineno
    filename = frame.f_code.co_filename
    fucname = frame.f_code.co_name
    return (filename, line_no, fucname)

if __name__ == "__main__":
    debug("test the debug log")
    trace("test the trace log")
    notice("test the notice log")
    warning("test the warning log")
    fatal("test the fatal log")
    init(log_path='./xxx_test')
    debug("test the debug log")
    trace("test the trace log")
    notice("test the notice log")
    warning("test the warning log")
    fatal("test the fatal log")

