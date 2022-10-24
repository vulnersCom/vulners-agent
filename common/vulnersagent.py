# -*- coding: utf-8 -*-
#
#  VULNERS OPENSOURCE
#  __________________
#
#  Vulners Project [https://vulners.com]
#  All Rights Reserved.
#
__author__ = "Kir Ermakov <isox@vulners.com>"

import vulners
from six import string_types


class AgentAPI(vulners.Vulners):

    # Vulners API Hostname
    vulners_hostname = "https://vulners.com"

    # Default URL's for the Vulners API.
    # Extension for Agent interfaces.

    api_endpoints = {
        'apiKey': "/api/v3/apiKey/valid/",
        'audit': "/api/v3/audit/audit/",
        'agent_register': "/api/v3/agent/register/",
        'agent_update': "/api/v3/agent/update/",
        'agent_audit': "/api/v3/agent/audit/",
        'agent_winsoftware': "/api/v3/agent/winsoftware",
        'supported_os': "/api/v3/agent/supported/"
    }

    def supported_os(self):
        return self.vulners_get_request('supported_os', {})

    def agent_register(self, agent_type, agent_version):
        """
        Tech Agent Register method
        :return: {'agentId':'AGENT_ID_STRING'}
        """
        if not isinstance(agent_type, string_types):
            raise TypeError("agent_type expected to be a string")
        if not isinstance(agent_version, string_types):
            raise TypeError("agent_version expected to be a string")
        return self.vulners_post_request('agent_register', {"agentType":agent_type, 'agentVersion':agent_version})

    def agent_update(self, agent_id, agent_type, agent_version, ipaddress, fqdn, macaddress, os_name, os_version, os_family, interface_list):
        """
        Tech Agent update information method
        :return: {"agent": agent dicted model}
        """
        if not isinstance(agent_id, string_types) or not agent_id:
            raise TypeError("agent_id expected to be a non empty string")
        if not isinstance(agent_version, string_types):
            raise TypeError("agent_version expected to be a string")
        if not isinstance(agent_type, string_types):
            raise TypeError("agent_type expected to be a string")
        if not isinstance(ipaddress, string_types):
            raise TypeError("ipaddress expected to be a string")
        if not isinstance(fqdn, string_types):
            raise TypeError("fqdn expected to be a string")
        if not isinstance(macaddress, string_types):
            raise TypeError("macaddress expected to be a string")
        if not isinstance(os_name, string_types):
            raise TypeError("os_name expected to be a string")
        if not isinstance(os_version, string_types):
            raise TypeError("os_version expected to be a string")
        if not isinstance(os_family, string_types):
            raise TypeError("os_family expected to be a string")
        if not isinstance(interface_list, list):
            raise TypeError("interface_list expected to be a list")
        return self.vulners_post_request('agent_update', {"agentType":agent_type,
                                                              'agentVersion':agent_version,
                                                              "agentId":agent_id,
                                                              "ipaddress":ipaddress,
                                                              "fqdn":fqdn,
                                                              "macaddress":macaddress,
                                                              "OSName":os_name,
                                                              "OSVersion":os_version,
                                                              "OSFamily":os_family,
                                                              "interfaces":interface_list,
                                                              })

    def agent_audit(self, agent_id, os, os_version, package):
        """
        Tech Agent Audit call

        :return: {'packages':[LIST OF VULNERABLE PACKAGES], 'reasons':LIST OF REASONS, 'vulnerabilities':[LIST OF VULNERABILITY IDs]}
        """
        if not isinstance(agent_id, string_types) or not agent_id:
            raise TypeError("agent_id expected to be a non empty string")
        if not isinstance(os, string_types):
            raise TypeError("OS expected to be a string")
        if not isinstance(os_version, string_types):
            raise TypeError("OS Version expected to be a string")
        if not isinstance(package, (list, set)):
            raise TypeError("Package expected to be a list or set")
        return self.vulners_post_request('agent_audit', {"os":os, 'version':os_version, 'package':package, 'agentId':agent_id})

    def agent_winaudit(self, agent_id, os, os_version, software):
        """
        Tech Agent Audit call

        :return: {'packages':[LIST OF VULNERABLE PACKAGES], 'reasons':LIST OF REASONS, 'vulnerabilities':[LIST OF VULNERABILITY IDs]}
        """
        if not isinstance(agent_id, string_types) or not agent_id:
            raise TypeError("agent_id expected to be a non empty string")
        if not isinstance(os, string_types):
            raise TypeError("OS expected to be a string")
        if not isinstance(os_version, string_types):
            raise TypeError("OS Version expected to be a string")
        if not isinstance(software, (list, set)):
            raise TypeError("Package expected to be a list or set")
        return self.vulners_post_request('agent_winsoftware', {"os":os, 'os_version':os_version, 'software':software, 'agentId':agent_id})


