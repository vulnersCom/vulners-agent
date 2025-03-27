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

from app import ClientApplication
from common import oscommands, osdetect


class Scanner(ClientApplication):

    singleton = True

    linux_package_commands = {
        "rpm": {
            "packages": """rpm -qa --qf '%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}\\n'""",
        },
        "deb": {
            "packages": """dpkg-query -W -f='${Status} ${Package} ${Version} ${Architecture}\n'|awk '($1 == "install" || $1 == "hold") && ($2 == "ok") {print $4" "$5" "$6}'""",
        },
        "apk": {
            "packages": """apk list -I""",
        },
        "apt": {
            "packages": """dpkg-query -W -f='${Status} ${Package} ${Version} ${Architecture}\n'|awk '($1 == "install" || $1 == "hold") && ($2 == "ok") {print $4" "$5" "$6}'"""
        },
    }

    def linux_scan(self, os_name, os_version, os_data):

        package_list = oscommands.execute(self.linux_package_commands[os_data["packager"]]["packages"]).splitlines()

        active_kernel = oscommands.execute("uname -r")

        # Package is: linux-headers-6.8.0-50-generic 6.8.0-50.51 amd64
        # Filtering disabled kernels
        packages = [
            package
            for package in package_list
            if not (package == "Listing..." or
               (package.startswith("kernel-") and not package.startswith("kernel-%s" % active_kernel)) or
               (package.startswith("linux-image-") and not package.startswith("linux-image-%s" % active_kernel))
            )
        ]
        agent_id = self.get_var("agent_id", namespace="shared")

        scan_results = self.vulners.agent_audit(agent_id=agent_id, os=os_name, os_version=os_version, package=packages)
        return scan_results

    def windows_scan(self, os_name, os_version, os_data, os_family="windows"):
        from common.winutils import get_windows_installed_software, get_windows_updates

        missing_kb, missing_updates, installed_kb, installed_updates = get_windows_updates()
        installed_software_list = get_windows_installed_software()
        software = []
        for name, version in installed_software_list.items():
            if re.match(r"^[\d+?.]+$", name.split()[-1]):
                name = " ".join(name.split()[:-1])
            software.append(
                {
                    "software": name,
                    "version": version,
                }
            )
        self.log.debug("Found missing KB's: %s" % missing_kb)
        self.log.debug("Enumerated Windows Software List: %s" % installed_software_list)
        agent_id = self.get_var("agent_id", namespace="shared")
        scan_results = self.vulners.agent_winaudit(
            agent_id=agent_id, os=os_data["osType"], os_version=os_version, software=software, kb_list=installed_kb
        )
        return scan_results

    def run(self):
        agent_id = self.get_var("agent_id", namespace="shared")
        if not agent_id:
            raise AssertionError("Can't run Scanner app without registered agent_id. Is Ticker online?")
        os_name, os_version, os_family = osdetect.get_os_parameters()
        self.log.debug("OS Detection complete: %s %s %s" % (os_name, os_version, os_family))

        # If it's not a Windows OS check for the compatibility
        if not os_family == "Windows":
            supported_os_lib = self.vulners.supported_os()["supported"]

            # Exit if OS is not supported in any way
            if os_name not in supported_os_lib:
                self.log.error(
                    "Can't perform scan request: Unknown OS %s. Supported os list: %s" % (os_name, supported_os_lib)
                )
                return

            os_data = supported_os_lib[os_name]
        else:
            os_data = {"osType": "windows"}

        if not hasattr(self, "%s_scan" % os_data["osType"]) or not callable(
            getattr(self, "%s_scan" % os_data["osType"], None)
        ):
            self.log.error("Can't scan this type of os: %s - no suitable scan method fount" % os_data["osType"])
            return

        scan_result = getattr(self, "%s_scan" % os_data["osType"])(
            os_name=os_name, os_version=os_version, os_data=os_data
        )

        self.log.debug("Scan complete: %s" % scan_result)
        last_scan_results = self.get_var("last_scan_results") or []
        last_scan_results.append(scan_result)
        self.set_var("last_scan_results", last_scan_results[:5])

        self.log.info("Scan complete. Check your result at https://vulners.com/scan")
