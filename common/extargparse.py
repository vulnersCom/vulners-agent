# -*- coding: utf-8 -*-
#
#  VULNERS OPENSOURCE
#  __________________
#
#  Vulners Project [https://vulners.com]
#  All Rights Reserved.
#
__author__ = "Kir Ermakov <isox@vulners.com>"

import argparse
import logging
import os
from os import access, W_OK, R_OK


LOG_LEVEL_STRINGS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']

def log_level_string_to_int(log_level_string):
    if not log_level_string in LOG_LEVEL_STRINGS:
        message = 'invalid choice: {0} (choose from {1})'.format(log_level_string, LOG_LEVEL_STRINGS)
        raise argparse.ArgumentTypeError(message)
    log_level_int = getattr(logging, log_level_string, logging.INFO)
    # check the logging log_level_choices have not changed from our expected values
    assert isinstance(log_level_int, int)
    return log_level_int

def log_file_valid_accessible(log_path_name):
    if not os.path.exists(log_path_name) or not access(log_path_name, W_OK):
        message = 'invalid file path: {0} Error: {1}'.format(log_path_name, "Path do not exist or is not write accessible.")
        raise argparse.ArgumentTypeError(message)
    return log_path_name

def config_file_exists_accessible(config_file_path_name):

    if not os.path.exists(config_file_path_name):
        message = 'invalid file path: {0} Error: {1}'.format(config_file_path_name,
                                                             "File do not exist.")
        raise argparse.ArgumentTypeError(message)

    if not access(config_file_path_name, R_OK):
        message = 'invalid file path: {0} Error: {1}'.format(config_file_path_name,
                                                             "File is not read accessible.")
        raise argparse.ArgumentTypeError(message)

    return config_file_path_name


class StoreDictKeyPair(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        self._nargs = nargs
        super(StoreDictKeyPair, self).__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        my_dict = {}
        for kv in values:
            k, v = kv.split("=")
            my_dict[k] = v
        setattr(namespace, self.dest, my_dict)