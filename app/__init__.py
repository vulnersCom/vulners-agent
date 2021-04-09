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
import sys
import logging
import base64
import json
import requests
import zlib
import time
import tempfile
from common.vulnersagent import AgentAPI
from common.configreader import get_full_config
from common.path import DATA_PATH
from random import randint
from six import string_types


class ClientApplication(object):
    if os.path.exists(DATA_PATH) is False:
        os.mkdir(DATA_PATH)
    data_file = os.path.join(DATA_PATH, 'application.data')
    singletone = False
    random_run_delay = True

    def __init__(self, config_file, log_level, log_path, inheritor_apps, ignore_proxy):
        self.initialized = False
        self.ignore_proxy = ignore_proxy
        # Set up logger namespace and levels
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.propagate = False
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.log.setLevel(log_level)
        if log_path:
            file_handler = logging.FileHandler(os.path.join(log_path, "%s.log" % self.__class__.__name__))
            file_handler.setFormatter(formatter)
            self.log.addHandler(file_handler)
        else:
            self.log.addHandler(console_handler)
        #
        self.log.debug("Application %s: Logger configured" % self.__class__.__name__)
        # Initing
        self.log.debug("Application %s: Init with config file %s" % (self.__class__.__name__, config_file))
        # Set up config file data
        full_config = get_full_config(config_file)
        self.config = full_config.get(self.__class__.__name__, full_config.get('DEFAULT'))
        self.log.debug("Application %s: Global config loaded %s" % (self.__class__.__name__, self.config))
        self.application_list = inheritor_apps
        self.log.debug("Application %s: Inherited apps loaded as %s" % (self.__class__.__name__, inheritor_apps))

    def singletone_init(self):
        flavor_id = self.__class__.__name__
        self.initialized = False

        basename = os.path.splitext(os.path.abspath(sys.argv[0]))[0].replace(
            "/", "-").replace(":", "").replace("\\", "-") + '-%s' % flavor_id + '.lock'

        self.lockfile = os.path.normpath(
            tempfile.gettempdir() + '/' + basename)

        self.log.debug("Application %s: SingleInstance lockfile: %s" % (self.__class__.__name__, self.lockfile))
        if sys.platform == 'win32':
            try:
                # file already exists, we try to remove (in case previous
                # execution was interrupted)
                if os.path.exists(self.lockfile):
                    os.unlink(self.lockfile)
                self.fd = os.open(
                    self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            except OSError:
                type, e, tb = sys.exc_info()
                if e.errno == 13:
                    message = "Application %s: Another instance is already running, quitting." % self.__class__.__name__
                    self.log.error(message)
                    raise RuntimeError(message)
                raise
        else:  # non Windows
            import fcntl
            self.fp = open(self.lockfile, 'w')
            self.fp.flush()
            try:
                fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                message = "Application %s: Another instance of %s is already running, quitting." % (self.__class__.__name__, self.__class__.__name__)
                self.log.warning(message)
                raise RuntimeError(message)
        self.initialized = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.singletone:
            if not self.initialized:
                return
            try:
                if sys.platform == 'win32':
                    if hasattr(self, 'fd'):
                        os.close(self.fd)
                        os.unlink(self.lockfile)
                else:
                    import fcntl
                    fcntl.lockf(self.fp, fcntl.LOCK_UN)
                    # os.close(self.fp)
                    if os.path.isfile(self.lockfile):
                        os.unlink(self.lockfile)
            except Exception as exc:
                self.log.error("Application %s: %s" % (self.__class__.__name__, exc))

    def apps(self, app_name):
        if app_name not in self.application_list:
            raise AssertionError("Can't make intercall to the app. Unknown name %s" % app_name)
        return self.application_list[app_name]

    def __encode_data(self, data):
        return zlib.compress(base64.b16encode(json.dumps(data).encode('utf-8')))

    def __decode_data(self, encoded_data):
        try:
            data = json.loads(base64.b16decode(zlib.decompress(encoded_data)))
        except Exception as exc:
            self.log.exception("Problems decoding data file %s" % exc)
            return {}
        return data

    def get_var(self, var_name, namespace = None):
        namespace = namespace or self.__class__.__name__
        shared_data = self.__read_data_file() or {}
        return shared_data.get(namespace, {}).get(var_name, None)

    def del_var(self, var_name, namespace = None):
        namespace = namespace or self.__class__.__name__
        shared_data = self.__read_data_file() or {}
        if var_name in shared_data.get(namespace, {}):
            shared_data.get(namespace, {}).pop(var_name)
            return self.__save_data_file(shared_data)
        return False

    def set_var(self, var_name, var_value, namespace = None):
        if type(var_value) not in [int, float, dict, list, None] and not isinstance(var_value, string_types):
            raise ValueError("Persistent variables can be only JSON compatible. Provided var type: %s" % type(var_value))
        namespace = namespace or self.__class__.__name__
        shared_data = self.__read_data_file() or {}
        shared_data[namespace] = shared_data.get(namespace) or {}
        shared_data[namespace][var_name] = var_value
        self.__save_data_file(shared_data)
        return var_value

    def __save_data_file(self, config_data):
        with open(self.data_file, 'wb') as data_file:
            data_file.write(self.__encode_data(config_data))
        self.log.debug("Application %s: Writing data file - %s" % (self.__class__.__name__, config_data))
        return True

    def __read_data_file(self):
        if not os.path.exists(self.data_file):
            self.log.info("There is no data file. Informational.")
            return None
        if not os.path.isfile(self.data_file) or not os.access(self.data_file, os.R_OK):
            self.log.error("Can't access data file at %s." % self.data_file)
            return None
        with open(self.data_file, 'rb') as data_file:
            config_data = self.__decode_data(data_file.read())
        self.log.debug("Application %s: Reading data file - %s" % (self.__class__.__name__, config_data))
        return config_data

    def countdown(self, sleep_time, step=1, msg='Sleeping'):  # in seconds
        try:
            pad_str = ' ' * len('%d' % step)
            for i in range(sleep_time, 0, -step):
                self.log.debug('Application %s: %s for the next %s seconds %s' % (self.__class__.__name__, msg, i, pad_str))
                time.sleep(step)
        except KeyboardInterrupt:
            self.log.debug('Application %s: Countdown interrupted' % self.__class__.__name__)
            time.sleep(1)
            return

    def run_app(self, parameters):
        self.log.debug("Application %s: Starting run. Singletone mode: %s" % (self.__class__.__name__, self.singletone))
        #
        if self.singletone:
            self.log.debug("Application %s: Init multiprocess singletone run lock" % self.__class__.__name__)
            self.singletone_init()
        #
        if self.random_run_delay:
            # Delay up to 5 minutes for running app
            random_sleep = randint(0, 60*5)
            self.log.debug("Application %s: Random sleep: %s" % (self.__class__.__name__, random_sleep))
            self.countdown(random_sleep)
        #
        # Set up Vulners connection lib
        # It placed here buti not in __init__ because of /api/v3/apiKey/valid/ call
        # Whet all agents all over the world are trying to check key for the validity - backend can die
        # So it's lazy init AFTER run delay
        AgentAPI.vulners_hostname = self.config.get('vulners_host') or 'https://vulners.com'
        api_key = self.config.get('api_key')
        agent_params = {'api_key': api_key}

        if self.ignore_proxy is False:
            agent_params.update({
                'proxies': {
                    'http': self.config.get('http_proxy') or os.environ.get('HTTP_PROXY'),
                    'https': self.config.get('https_proxy') or os.environ.get('HTTPS_PROXY')
                }
            })
        try:
            self.vulners = AgentAPI(**agent_params)
        except requests.ConnectionError as connection_error:
            message = 'Failed to establish connection to Vulners host at %s: %s' % (
            AgentAPI.vulners_hostname, connection_error)
            self.log.error(message)
            raise EnvironmentError(
                'Failed to establish connection to Vulners host at %s' % AgentAPI.vulners_hostname)
        self.log.debug("Application %s: Init Vulners API with key %s" % (self.__class__.__name__, api_key))

        run_data = {
            'app_name': self.__class__.__name__,
            'run_parameters': parameters,
            'run_result': None,
            'success': False,
            'exception': None,
            'exectime': 0,
        }

        start_time = int(round(time.time() * 1000))
        try:
            run_result = self.run(**parameters)
            self.log.debug("Application %s: Run finished with no exceptions" % self.__class__.__name__)
            run_data['success'] = True
            run_data['run_result'] = run_result
        except Exception as exc:
            self.log.exception("Failed running application %s with Excpention:\n %s" % (self.__class__.__name__, exc))
            run_data['success'] = False
            run_data['exception'] = "%s" % exc
        end_time = int(round(time.time() * 1000))
        run_data['exectime'] = end_time - start_time
        self.log.debug("Application %s: Run complete: %s" % (self.__class__.__name__, run_data))
        return run_data

    def run(self, *args, **kwargs):
        pass
