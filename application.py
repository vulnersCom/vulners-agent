#! /usr/bin/env python3.6
# -*- coding: utf-8 -*-
#
#  VULNERS OPENSOURCE
#  __________________
#
#  Vulners Project [https://vulners.com]
#  All Rights Reserved.
#
__author__ = "Kir Ermakov <isox@vulners.com>"

from common.path import PROJECT_ROOT_PATH
from common.extargparse import *
import app
from common.modloader import get_inheritors

def available_apps(app_name):

    available_applications = get_inheritors(app, app.ClientApplication)
    if not app_name in available_applications:
        message = 'invalid file path: {0} Error: {1}'.format(app_name,
                                                             "Application do not exist. Available apps: %s" % ', '.join(available_applications.keys()))
        raise argparse.ArgumentTypeError(message)
    return app_name

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Vulners Agent ticker script')
    parser.add_argument('--loglevel', default='INFO', type=log_level_string_to_int, nargs='?',
                        help='Application log level. %s' % LOG_LEVEL_STRINGS)

    parser.add_argument('--logpath', type=log_file_valid_accessible, nargs='?', default=None,
                        help='Application log file to save logger output')

    default_config_dir = os.path.join(PROJECT_ROOT_PATH, 'config', 'vulners_agent.conf')
    parser.add_argument('--config', type=config_file_exists_accessible, nargs='?', default = default_config_dir,
                        help='Application config file location')

    parser.add_argument('--app', type=available_apps, nargs='?', default=None, required=True,
                        help='Application name to run')

    parser.add_argument("--params", dest="parameters", action=StoreDictKeyPair, nargs="+", metavar="KEY=VAL", default={})

    args = parser.parse_args()

    # Initialize applications
    inheritors = get_inheritors(app, app.ClientApplication)
    initialized_inheritors = {}
    init_args = {

        'config_file': args.config,
        'log_level': args.loglevel,
        'log_path': args.logpath,
        'inheritor_apps': inheritors,
    }
    for app_name in inheritors:
        inheritors[app_name] = inheritors[app_name](**init_args)
    current_application = inheritors[args.app]
    # Run application
    current_application.run_app(args.parameters)
