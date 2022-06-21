# -*- coding: utf-8 -*-
#
#  VULNERS OPENSOURCE
#  __________________
#
#  Vulners Project [https://vulners.com]
#  All Rights Reserved.
#
__author__ = "Kir Ermakov <isox@vulners.com>"

import re

import distro
from getmac import get_mac_address
import socket
from common.oscommands import execute
import ifaddr
from collections import defaultdict
import concurrent.futures
import platform
from common.stringops import remove_non_ascii

LOOPBACK = ['127.0.0.1', '0:0:0:0:0:0:0:1']


def get_os_parameters():
    # Gather meta information about the system

    # Get OS family
    platform_family = platform.system()

    if platform_family == 'Windows':
        from common.winutils import get_windows_data
        win_version = get_windows_data()
        return remove_non_ascii(win_version["name"]), win_version["version"], platform_family

    platform_id = distro.id()
    platform_version = distro.version()

    # In most cases this info will be valid, but there is some list of exclusions

    # If it's a Darwin, this is probably Mac OS. We need to get visible version using 'sw_vers' command
    if platform_id.lower() == 'darwin':
        os_params = execute('sw_vers').splitlines()
        platform_id = os_params[0].split(":")[1].strip()
        platform_version = os_params[1].split(":")[1].strip()
        return platform_id, platform_version, 'macos'

    if platform_id == "altlinux":
        platform_id = "alt linux"
        platform_version = _parse_altlinux_version(platform_version)
        return platform_id, platform_version, platform_family

    return platform_id, platform_version, platform_family


def _parse_altlinux_version(platform_version: str) -> str:
    match = re.search("^(?P<major>\d+)\.", platform_version)
    return match.group("major")


def get_interface_data(interface_name, ipaddress):
    macaddress = (get_mac_address(interface=interface_name) or get_mac_address(ip=ipaddress,
                                                                               network_request=True) or "NONE")
    macaddress = macaddress.upper()
    return {
        "ifaceName": interface_name,
        'ipaddress': ipaddress,
        'macaddress': macaddress
    }


def get_interface_list():
    active_interfaces = defaultdict(list)

    active_v4_interfaces = defaultdict(list)
    for adapter in ifaddr.get_adapters():
        for ipaddress in adapter.ips:
            # If it's ipv4, it's a string. ipv6 is a tuple
            if isinstance(ipaddress.ip, str) and ipaddress.ip not in LOOPBACK:
                active_v4_interfaces[adapter.nice_name].append(ipaddress.ip)
    # If there is no take ipv6 instead
    if not active_v4_interfaces:
        for adapter in ifaddr.get_adapters():
            for ipaddress in adapter.ips:
                # If it's ipv4, it's a string. ipv6 is a tuple
                if not isinstance(ipaddress.ip, str) and ipaddress.ip[0] not in LOOPBACK:
                    active_interfaces[adapter.nice_name].append(ipaddress.ip[0])
    else:
        active_interfaces = active_v4_interfaces

    interface_list = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(active_interfaces)) as executor:
        app_exec_pool = [executor.submit(get_interface_data, interface_name, active_interfaces[interface_name][0]) for
                         interface_name in active_interfaces]
        for future in concurrent.futures.as_completed(app_exec_pool):
            interface_list.append(future.result())
    for interface in interface_list:
        for key in interface:
            interface[key] = remove_non_ascii(interface[key])
    return interface_list


def get_ip_mac_fqdn():
    interfaces = get_interface_list()

    primary_interface = sorted(interfaces, key=lambda k: k['ifaceName'])[0]
    ip_address = primary_interface['ipaddress']
    fqdn = socket.getaddrinfo(socket.gethostname(), 0, 0, 0, 0, socket.AI_CANONNAME)[0][3]
    mac_address = primary_interface['macaddress']
    return ip_address, mac_address, fqdn
