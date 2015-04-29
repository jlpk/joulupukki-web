import logging

import os

import pecan



from joulupukki.common.datamodel.job import Job


def get_logger(build, distro=None):
    log_file = os.path.join(pecan.conf.workspace_path,
                            build.username,
                            build.project_name,
                            'builds',
                            str(build.id_),
                            "log.txt")
    logger = logging.getLogger("#".join(("Builder", str(build.id_))))
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


def get_logger_path(build):
    log_file = os.path.join(pecan.conf.workspace_path,
                            build.username,
                            build.project_name,
                            'builds',
                            str(build.id_),
                            "log.txt")
    return log_file


def get_logger_from_path(path, id_):
    logger = logging.getLogger("#".join(("Builder", id_)))
    # create formatter
    formatter = logging.Formatter('[%(msecs)d] [%(levelname)-5.5s] [%(name)s] %(message)s')
    # create logger
    logger.setLevel(logging.DEBUG)
    # create file handler and set level to debug
    ch = logging.FileHandler(path)
    ch.setLevel(logging.DEBUG)

    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    # return logger
    return logger


def get_logger_docker(job):
    job_folder = job.get_folder_path()
    log_file = os.path.join(job_folder,
                            "log.txt")
    logger = logging.getLogger("#".join(("Docker", str(job.build_id), str(job.id_), job.distro)))
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


def get_logger_job(job):
    job_folder = job.get_folder_path()
    log_file = os.path.join(job_folder,
                            "log.txt")
    logger = logging.getLogger("#".join(("Job", str(job.build_id), str(job.id_), job.distro)))
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
