# -*- coding: utf-8 -*-
#
#  VULNERS OPENSOURCE
#  __________________
#
#  Vulners Project [https://vulners.com]
#  All Rights Reserved.
#
__author__ = "Kir Ermakov <isox@vulners.com>"

from app import ClientApplication
from common import __version__ as __agent_version__, __agent_type__
from common import osdetect
from pytimeparse.timeparse import timeparse
import arrow
import datetime
import pytz
import concurrent.futures
import six
import time


class Ticker(ClientApplication):

    singletone = True

    minimum_task_interval = '5m'

    max_threads = 10

    default_schedule = [

        {
            'app_name':'Scanner',
            'interval':'1h',
            'run_parameters':{},
            'last_run':arrow.get(1970, 12, 12).timestamp,
            'run_now':False,
        },

    ]

    def process_schedule(self, schedule_list):
        application_run_list = []
        for application_schedule in schedule_list:
            if application_schedule['app_name'] not in self.application_list:
                continue
            # Don't use intervals less that minimum_task_interval
            interval_seconds = max(timeparse(application_schedule['interval']), timeparse(self.minimum_task_interval))

            # Unix timestamp in UTC, seconds
            # Python version awareness
            if six.PY2:
                timestamp_now = time.mktime(datetime.datetime.now(pytz.utc).timetuple())
            else:
                timestamp_now = int(datetime.datetime.now(pytz.utc).timestamp())

            timestamp_diff = timestamp_now - application_schedule['last_run']

            if (timestamp_diff > interval_seconds) or application_schedule['run_now']:
                self.log.debug("Application %s time diff %s more than %s, run now flag is %s. Schedule it to run." % (application_schedule['app_name'], timestamp_diff, interval_seconds, application_schedule['run_now']))
                application_schedule['run_now'] = False
                application_run_list.append((application_schedule['app_name'], application_schedule['run_parameters']))
                application_schedule['last_run'] = timestamp_now

        # Run tasks in different threads. Usually we don't need results of run_now.
        app_run_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            app_exec_pool = [executor.submit(self.apps(app_name).run_app, app_run_parameters) for app_name, app_run_parameters in application_run_list]
            for future in concurrent.futures.as_completed(app_exec_pool):
                app_run_results.append(future.result())

        return schedule_list

    def run(self):
        # Let's check up that this agent is registered
        agent_id = self.get_var('agent_id', namespace='shared')
        if not agent_id:
            self.log.debug("Unregistered agent. Gathering Agent ID from Vulners")
            registration = self.vulners.agent_register(agent_type= __agent_type__, agent_version= __agent_version__)
            if 'agentId' not in registration:
                message = 'Failed to get Agent ID from Vulners API: %s' % registration
                self.log.error(message)
                raise AssertionError(message)
            agent_id = self.set_var('agent_id', registration['agentId'], namespace='shared')
            self.log.debug("Registered as %s" % registration['agentId'])
        # Update agent information, forming and sending 'ping' data
        self.log.debug("Agent ID: %s" % agent_id)
        ip_address, mac_address, fqdn = osdetect.get_ip_mac_fqdn()
        self.log.debug("IP Address detected as: '%s' with MAC '%s' and Hostname '%s'" % (ip_address, mac_address, fqdn))
        os_name, os_version, os_family = osdetect.get_os_parameters()
        self.log.debug("OS Name: '%s' with version '%s'" % (os_name, os_version))
        update_result = self.vulners.agent_update(agent_id = agent_id,
                                                  agent_type = __agent_type__,
                                                  agent_version = __agent_version__,
                                                  ipaddress = self.config.get('ip_address') or ip_address,
                                                  fqdn = self.config.get('fqdn') or fqdn,
                                                  macaddress = self.config.get('mac_address') or mac_address,
                                                  os_name = os_name,
                                                  os_version = os_version,
                                                  os_family = os_family,
                                                  interface_list=osdetect.get_interface_list(),
                                                  )
        if 'agent' not in update_result:
            if update_result.get('errorCode') == 163:
                self.log.error("Corrupted agent_id. Renewing on the next run.")
                self.del_var('agent_id', namespace='shared')
                return
            # Unexpected error
            raise AssertionError("Failed to get agent data from Vulners host. Received Vulners response: %s" % update_result)
        self.log.debug("Vulners Agent Update response: %s" % update_result)
        self.set_var('agent', update_result['agent'], namespace='shared')
        schedule = self.get_var('schedule') or self.default_schedule
        self.log.debug("Starting to process schedule: %s" % schedule)
        schedule = self.process_schedule(schedule)
        self.log.debug("Schedule processed. Updated schedule: %s" % schedule)
        self.set_var('schedule', schedule)
