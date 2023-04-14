#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#  VULNERS OPENSOURCE
#  __________________
#
#  Vulners Project [https://vulners.com]
#  All Rights Reserved.
#
__author__ = "Kir Ermakov <isox@vulners.com>"

import sys
from common.path import DEFAULT_CONFIG_PATH, DEPENDENCIES_PATH

sys.path.append(DEPENDENCIES_PATH)

import app
from common.extargparse import *
from common.modloader import get_inheritors


def available_apps(app_name):

    available_applications = get_inheritors(app, app.ClientApplication)
    if app_name not in available_applications:
        message = 'invalid file path: {0} Error: {1}'.format(
            app_name, "Application do not exist. Available apps: %s" % ', '.join(available_applications.keys())
        )
        raise argparse.ArgumentTypeError(message)
    return app_name


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Vulners Agent ticker script')
    parser.add_argument('--loglevel', default='INFO', type=log_level_string_to_int, nargs='?',
                        help='Application log level. %s' % LOG_LEVEL_STRINGS)

    parser.add_argument('--logpath', type=log_file_valid_accessible, nargs='?', default=None,
                        help='Application log file to save logger output')

    parser.add_argument('--log_max_bytes', type=int, nargs='?', default=None,
                        help='Max log file size (bytes)')

    parser.add_argument('--log_backup_count', type=int, nargs='?', default=None,
                        help='Max log file count')

    parser.add_argument('--config', type=config_file_exists_accessible, nargs='?', default=DEFAULT_CONFIG_PATH,
                        help='Application config file location')

    parser.add_argument('--app', type=available_apps, nargs='?', default=None, required=True,
                        help='Application name to run')

    parser.add_argument("--params", dest="parameters", action=StoreDictKeyPair, nargs="+",
                        metavar="KEY=VAL", default={})

    parser.add_argument('--ignore-proxy', default=False, const=True, nargs='?',
                        help='Ignore proxy configuration and environment')

    parser.add_argument('--data_dir', type=data_dir_exists_accessible, nargs='?', default=None,
                        help='Application data directory location')

    args = parser.parse_args()

    # Initialize applications
    inheritors = get_inheritors(app, app.ClientApplication)
    initialized_inheritors = {}

    init_args = {
        'config_file': args.config,
        'log_level': args.loglevel,
        'log_path': args.logpath,
        'log_max_bytes': args.log_max_bytes,
        'log_backup_count': args.log_backup_count,
        'ignore_proxy': args.ignore_proxy,
        'inheritor_apps': inheritors,
        'data_dir': args.data_dir
    }

    for app_name in inheritors:
        inheritors[app_name] = inheritors[app_name](**init_args)
    current_application = inheritors[args.app]

    # Check is there agent_id already set, set it if there is no agent_id
    if args.app != 'Ticker':
        ticker_app = inheritors['Ticker']
        with ticker_app as ticker_app_wrapper:
            agent_id = ticker_app_wrapper.get_var('agent_id', namespace='shared')
            if not agent_id:
                ticker_app_wrapper.run_app(args.parameters)

    # Run application and finish it always with __exit__ method to remove file locks
    with current_application as app_wrapper:
        app_wrapper.run_app(args.parameters)
