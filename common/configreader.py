# -*- coding: utf-8 -*-
#
#  VULNERS OPENSOURCE
#  __________________
#
#  Vulners Project [https://vulners.com]
#  All Rights Reserved.
#
__author__ = "Kir Ermakov <isox@vulners.com>"

from configparser import ConfigParser


def get_config(full_file_path):
    config = ConfigParser()
    config.read(full_file_path)
    return config


def get_full_config(full_file_path):
    config = get_config(full_file_path)
    config_data = {s: dict(config.items(s)) for s in config.sections()}
    config_data.update({"DEFAULT": dict((key, config["DEFAULT"].get(key)) for key in config["DEFAULT"])})
    return config_data


def get_vulners_api_key(full_file_path):
    config = get_config(full_file_path)
    api_key = config["DEFAULT"].get("api_key", "")
    return api_key
