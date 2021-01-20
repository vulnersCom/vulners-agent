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

import app
from common.path import DEFAULT_CONFIG_PATH, DEPENDENCIES_PATH
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
    import sys
    sys.path.append(DEPENDENCIES_PATH)

    parser = argparse.ArgumentParser(description='Vulners Agent ticker script')
    parser.add_argument('--loglevel', default='INFO', type=log_level_string_to_int, nargs='?',
                        help='Application log level. %s' % LOG_LEVEL_STRINGS)

    parser.add_argument('--logpath', type=log_file_valid_accessible, nargs='?', default=None,
                        help='Application log file to save logger output')

    parser.add_argument('--config', type=config_file_exists_accessible, nargs='?', default=DEFAULT_CONFIG_PATH,
                        help='Application config file location')

    parser.add_argument('--app', type=available_apps, nargs='?', default=None, required=True,
                        help='Application name to run')

    parser.add_argument("--params", dest="parameters", action=StoreDictKeyPair, nargs="+",
                        metavar="KEY=VAL", default={})

    parser.add_argument('--ignore-proxy', default=False, const=True, nargs='?',
                        help='Ignore proxy configuration and environment')

    args = parser.parse_args()

    # Initialize applications
    inheritors = get_inheritors(app, app.ClientApplication)
    initialized_inheritors = {}

    init_args = {
        'config_file': args.config,
        'log_level': args.loglevel,
        'log_path': args.logpath,
        'ignore_proxy': args.ignore_proxy,
        'inheritor_apps': inheritors,
    }

    for app_name in inheritors:
        inheritors[app_name] = inheritors[app_name](**init_args)
    current_application = inheritors[args.app]
    # Run application
    current_application.run_app(args.parameters)
