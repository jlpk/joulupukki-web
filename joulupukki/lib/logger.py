import logging

import os

import pecan




def get_logger(uuid):
    log_file = os.path.join(pecan.conf.tmp_path, uuid, "log.txt")
    # create logger
    logger = logging.getLogger("Builder#" + uuid)
    logger.setLevel(logging.DEBUG)
    # create file handler and set level to debug
    ch = logging.FileHandler(log_file)
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)-5.5s] [%(name)s] %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    # return logger
    return logger



def get_logger_docker(uuid):
    log_file = os.path.join(pecan.conf.tmp_path, uuid, "log.txt")
    # create logger
    logger = logging.getLogger("Docker#" + uuid)
    logger.setLevel(logging.DEBUG)
    # create file handler and set level to debug
    ch = logging.FileHandler(log_file)
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    # return logger
    return logger
