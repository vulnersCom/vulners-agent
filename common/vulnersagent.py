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


class AgentAPI(vulners.VulnersApi):

    supported_os = vulners.base.Endpoint(
        method="get",
        url="/api/v3/agent/supported/",
        params=[]
    )

    register_agent = vulners.base.Endpoint(
        method="post",
        url="/api/v3/agent/register/",
        params=[("agentType", vulners.base.String()), ("agentVersion", vulners.base.String())]
    )

    audit_agent = vulners.base.Endpoint(
        method="post",
        url="/api/v3/agent/audit/",
        params=[
            ("os", vulners.base.String()),
            ("version", vulners.base.String()),
            ("package", vulners.base.List()),
            ("agentId", vulners.base.String()),
        ]
    )

    update_agent = vulners.base.Endpoint(
        method="post",
        url="/api/v3/agent/update/",
        params=[
            ("agentType", vulners.base.String()),
            ("agentVersion", vulners.base.String()),
            ("agentId", vulners.base.String()),
            ("ipaddress", vulners.base.String()),
            ("fqdn", vulners.base.String()),
            ("macaddress", vulners.base.String()),
            ("OSName", vulners.base.String()),
            ("OSVersion", vulners.base.String()),
            ("OSFamily", vulners.base.String()),
            ("interfaces", vulners.base.List()),
            ("tags", vulners.base.String(allow_null=True)),
        ]
    )

    winsoftware_agent = vulners.base.Endpoint(
        method="post",
        url="/api/v3/agent/winsoftware",
        params=[
            ("os", vulners.base.String()),
            ("os_version", vulners.base.String()),
            ("software", vulners.base.String()),
            ("kb_list", vulners.base.List()),
            ("agentId", vulners.base.List()),
        ]
    )

    def agent_register(self, agent_type, agent_version):
        """
        Tech Agent Register method
        :return: {'agentId':'AGENT_ID_STRING'}
        """
        if not isinstance(agent_type, string_types):
            raise TypeError("agent_type expected to be a string")
        if not isinstance(agent_version, string_types):
            raise TypeError("agent_version expected to be a string")
        return self.register_agent(
            agentType=agent_type, agentVersion=agent_version
        )

    def agent_update(
        self,
        agent_id,
        agent_type,
        agent_version,
        ipaddress,
        fqdn,
        macaddress,
        os_name,
        os_version,
        os_family,
        interface_list,
        tags
    ):
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
        return self.update_agent(
            agentType=agent_type,
            agentVersion=agent_version,
            agentId=agent_id,
            ipaddress=ipaddress,
            fqdn=fqdn,
            macaddress=macaddress,
            OSName=os_name,
            OSVersion=os_version,
            OSFamily=os_family,
            interfaces=interface_list,
            tags=tags
        )

    def agent_audit(self, agent_id, os, os_version, package):
        """
        Tech Agent Audit call

        :return: {
            'packages':[LIST OF VULNERABLE PACKAGES],
            'reasons':LIST OF REASONS,
             'vulnerabilities':[LIST OF VULNERABILITY IDs]
        }
        """
        if not isinstance(agent_id, string_types) or not agent_id:
            raise TypeError("agent_id expected to be a non empty string")
        if not isinstance(os, string_types):
            raise TypeError("OS expected to be a string")
        if not isinstance(os_version, string_types):
            raise TypeError("OS Version expected to be a string")
        if not isinstance(package, (list, set)):
            raise TypeError("Package expected to be a list or set")

        return self.audit_agent(os=os, version=os_version, package=package, agentId=agent_id)

    def agent_winaudit(self, agent_id, os, os_version, software, kb_list):
        """
        Tech Agent Audit for Windows OS call

        :return: {
            'packages':[LIST OF VULNERABLE PACKAGES],
            'reasons':LIST OF REASONS,
            'vulnerabilities':[LIST OF VULNERABILITY IDs]
        }
        """
        if not isinstance(agent_id, string_types) or not agent_id:
            raise TypeError("agent_id expected to be a non empty string")
        if not isinstance(os, string_types):
            raise TypeError("OS expected to be a string")
        if not isinstance(os_version, string_types):
            raise TypeError("OS Version expected to be a string")
        if not isinstance(software, (list, set)):
            raise TypeError("Software expected to be a list or set")
        if not isinstance(kb_list, (list, set)):
            raise TypeError("Installed KB expected to be a list or set")

        return self.agent_winaudit(
            agent_id=agent_id,
            os=os,
            os_version=os_version,
            software=software,
            kb_list=kb_list
        )
