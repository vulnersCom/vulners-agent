# -*- coding: utf-8 -*-
#
#  VULNERS OPENSOURCE
#  __________________
#
#  Vulners Project [https://vulners.com]
#  All Rights Reserved.
#
__author__ = "Kir Ermakov <isox@vulners.com>"

import os

DEFAULT_CONFIG_PATH = "/etc/vulners/vulners_agent.conf"
PROJECT_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(PROJECT_ROOT_PATH, "data")
DEPENDENCIES_PATH = os.path.join(PROJECT_ROOT_PATH, "dependencies")
