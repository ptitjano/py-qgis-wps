#
# Copyright 2018 3liz
# Author: David Marteau
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
""" Logger
"""
import os
import sys
import logging
from contextlib import contextmanager

from .config import confservice

LOGGER = logging.getLogger('SRVLOG')

REQ_LOG_TEMPLATE = u"{ip}\t{code}\t{method}\t{url}\t{time}\t{length}\t"
REQ_FORMAT = REQ_LOG_TEMPLATE + '{agent}\t{referer}'
RREQ_FORMAT = REQ_LOG_TEMPLATE

# Lies between warning and error
REQ = 21
RREQ = 22

FORMATSTR = '%(asctime)s\t[%(process)d]\t%(levelname)s\t%(message)s'


def configure_log_levels():
    logging.addLevelName(REQ, "REQ")
    logging.addLevelName(RREQ, "RREQ")


def setup_log_handler(log_level: str = None):
    """ Initialize log handler with the given log level
    """
    configure_log_levels()

    logger = LOGGER
    formatstr = FORMATSTR
#   formatstr = '%(asctime)s] [%(levelname)s] file=%(pathname)s line=%(lineno)s '
#               'module=%(module)s function=%(funcName)s %(message)s'

    log_level = log_level or confservice.get('logging', 'level', fallback='debug')
    logger.setLevel(getattr(logging, log_level.upper()))
    channel = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(formatstr)
    channel.setFormatter(formatter)
    logger.addHandler(channel)


@contextmanager
def logfile_context(workdir: str, basename: str):
    """ Add a temporary file handler
    """
    logfile = os.path.join(workdir, "%s.log" % basename)
    channel = logging.FileHandler(logfile)
    formatter = logging.Formatter(FORMATSTR)
    channel.setFormatter(formatter)
    LOGGER.addHandler(channel)
    try:
        yield
    finally:
        LOGGER.removeHandler(channel)
        channel.close()


def format_log_request(handler):
    """ Format current request from the given tornado request handler

        :return a tuple (fmt,code,reqtime,length) where:
            fmt: the log string
            code: the http return code
            reqtime: the request time
            length: the size of the payload
    """
    request = handler.request
    code = handler.get_status()
    reqtime = request.request_time()

    length = handler._headers.get('Content-Length') or -1
    agent = request.headers.get('User-Agent') or ""
    referer = request.headers.get('Referer') or ""

    fmt = REQ_FORMAT.format(
        ip=request.remote_ip,
        method=request.method,
        url=request.uri,
        code=code,
        time=int(1000.0 * reqtime),
        length=length,
        referer=referer,
        agent=agent)

    return fmt, code, reqtime, length


def log_request(handler):
    """ Log the current request

        :param code: The http return code
        :param reqtiem: The request time

        :return A tuple (code,reqtime,length) where:
            code: the http retudn code
            reqtime: the request time
            length: the size of the payload
    """
    fmt, code, reqtime, length = format_log_request(handler)
    LOGGER.log(REQ, fmt)
    return code, reqtime, length


def format_log_rrequest(response):
    """ Format current r-request from the given response

        :param response: The response returned from the request
        :param checksum: Add an md5 checksum for the urlS

        :return A tuple (fmt,code,reqtime,length) where:
            fmt: the log string
            code: the http retudn code
            reqtime: the request time
            length: the size of the payload
    """
    request = response.request
    code = response.code
    reqtime = response.request_time

    length = -1
    try:
        length = response.headers['Content-Length']
    except KeyError:
        pass

    fmt = RREQ_FORMAT.format(
        ip='',
        method=request.method,
        url=request.url,
        code=code,
        time=int(1000.0 * reqtime),
        length=length)

    return fmt, code, reqtime, length


def log_rrequest(response):
    """ Log the current response request from the given response

        :return A tuple (code,reqtime,length) where:
            code: the http retudn code
            reqtime: the request time
            length: the size of the payload
    """
    fmt, code, reqtime, length = format_log_rrequest(response)
    LOGGER.log(RREQ, fmt)
    return code, reqtime, length
