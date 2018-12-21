# -*- coding:utf8 -*-

import logging
import json
import os

def config(conf):
    log_level_set = ('debug', 'info', 'warning', 'error', 'critical')
    
    log_path = conf.get("log_path", ".")
    log_name = conf.get("log_name", "DEFAULT.LOG")
    log_level = conf.get("log_level", "debug")
    log_format = conf.get("log_format", "[%(levelname)s][%(filename)s][%(asctime)s] %(message)s")

    if log_level == "info":
        level = logging.INFO
    elif log_level == "warning":
        level = logging.WARNING
    elif log_level == "error":
        level = logging.ERROR
    elif log_level == "critical":
        level = logging.CRITICAL
    else:
        level = logging.DEBUG

    if log_level not in log_level_set:
        logging.warning(log_level + ": invalid log level.")

    logging.basicConfig(filename=os.path.join(log_path, log_name), level=level, format=log_format)

def configFile(filepath):
    """
    {
        "log_path": ".",
        "log_name": "default.log",
        "log_level"; "debug",
        "log_format": "[%(levelname)s][%(filename)s][%(asctime)s] %(message)s"
    }
    """
    if not os.path.isfile(filepath):
        logging.warning(filepath + ": No such file")
        return
    with open(filepath) as f:
        d = f.read()
        
        try:
            conf = json.loads(d)
        except Exception as e:
            logging.warning("Load json configure file fail." + str(e))
            return
        config(conf)

def debug(msg):
    msg = msg
    logging.debug(msg)

def info(msg):
    logging.info(msg)

def warning(msg):
    logging.warning(msg)

def error(msg):
    logging.error(msg)

def critical(msg):
    logging.critical(msg)

if __name__ == "__main__":
    conf = {
        "log_path": ".",
        "log_name": "default.log",
        "log_level": "debug",
        "log_format": "[%(levelname)s][%(filename)s][%(asctime)s] %(message)s"
    }
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        sys.stdout.write(json.dumps(conf, indent=2))
    else:
        config(conf)

        debug("测试")
        info("This is a info log message")
        warning("This is a warning message")
        error("This is a error log message")
        critical("This is a critical log message")
