# -*- coding: utf-8 -*-
#
#  VULNERS OPENSOURCE
#  __________________
#
#  Vulners Project [https://vulners.com]
#  All Rights Reserved.
#
__author__ = "Kir Ermakov <isox@vulners.com>"

from . import ClientApplication
import os
from os import access, R_OK
from common.configreader import get_full_config


class Migration(ClientApplication):

    random_run_delay = False
    singletone = True

    def run(self, old_config_file, old_version):
        # Check that config gile do exist
        if not os.path.exists(old_config_file) or not access(old_config_file, R_OK):
            raise AttributeError("Can't read old configuration file at path %s. It does not exist or it is not readable" % old_config_file)

        # Migration config from 0.2 version
        # application.py --app Migration --params old_config_file=/tmp/old_config.conf old_version=0.2
        if old_version == '0.2':
            config_data = get_full_config(old_config_file)
            if not config_data.get('agent'):
                raise AssertionError('Misconfigured old configuration file: %s' % config_data)
            self.log.debug("Successfully parsed config file: %s" % config_data)
            agent_id = config_data.get('agent').get('agent_id')
            if not agent_id:
                self.log.warning("There is no agent_id provided in old config file. Passing.")
                return
            self.set_var('agent_id', agent_id, namespace='shared')
            self.log.debug("Successfully migrated agent_id: %s" % agent_id)
            return
