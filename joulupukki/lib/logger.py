import logging

import os

import pecan




def get_logger(uuid, distro=None):
    log_file = os.path.join(pecan.conf.builds_path, uuid, "log.txt")
    logger = logging.getLogger("#".join(("Builder", uuid)))
    # create formatter
    formatter = logging.Formatter('[%(msecs)d] [%(levelname)-5.5s] [%(name)s] %(message)s')
    # create logger
    logger.setLevel(logging.DEBUG)
    # create file handler and set level to debug
    ch = logging.FileHandler(log_file)
    ch.setLevel(logging.DEBUG)

    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    # return logger
    return logger



def get_logger_docker(uuid, distro):
    log_file = os.path.join(pecan.conf.builds_path, uuid, distro, "log.txt")
    logger = logging.getLogger("#".join(("Docker", uuid, distro)))
    # create logger
    logger.setLevel(logging.DEBUG)
    # create file handler and set level to debug
    ch = logging.FileHandler(log_file)
    ch.setLevel(logging.DEBUG)
    # create formatter
    #formatter = logging.Formatter('[%(asctime)s] %(message)s')
    formatter = logging.Formatter('%(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    # return logger
    return logger
