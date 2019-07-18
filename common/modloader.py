# -*- coding: utf-8 -*-
#
#  VULNERS OPENSOURCE
#  __________________
#
#  Vulners Project [https://vulners.com]
#  All Rights Reserved.
#
__author__ = "Kir Ermakov <isox@vulners.com>"
import pkgutil
import inspect
from pip._internal import main as pip


def get_inheritors(module, inheritor):
    members = set()
    for mod_path, mod_name, is_pkg in pkgutil.iter_modules(module.__path__):
        # find all classed inherited from scanner.osDetect.ScannerInterface in all files
        members = members.union(
            inspect.getmembers(__import__('%s.%s' % (module.__name__, mod_name), fromlist=[module.__name__]),
                               lambda member: inspect.isclass(member)
                                              and issubclass(member, inheritor)
                                              and member.__module__ == '%s.%s' % (module.__name__, mod_name)
                                              and member !=  inheritor))
    return dict((member[0], member[1]) for member in members)
