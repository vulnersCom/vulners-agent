#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'videns'
import inspect
import pkgutil
import json
import os

import logging
import sys

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2


try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

import scanModules


VULNERS_LINKS = {'pkgChecker':'/api/v3/agent/audit/',
                 'bulletin':'/api/v3/search/id/',
                 'agentRegister':'/api/v3/agent/register/',
                 'agentUpdate':'/api/v3/agent/update/'}


AGENT_TYPE = "vulners_agent"
AGENT_VERSION = "0.2"
HTTP_PROXY = None
API_HOST = None
logfile = os.path.realpath(os.path.join(os.path.dirname(__file__),"logs/vulners.log"))


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", filename=logfile)

logger = logging.getLogger("main")



def sendHttpRequest(url, payload):
    if HTTP_PROXY:
        opener = urllib2.build_opener(
            urllib2.HTTPHandler(),
            urllib2.HTTPSHandler(),
            urllib2.ProxyHandler({'https': HTTP_PROXY}))
        urllib2.install_opener(opener)
    req = urllib2.Request("https://%s%s" % (API_HOST, url))
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', '%s-v%s' % (AGENT_TYPE, AGENT_VERSION))
    logger.debug("Sending http request, url - %s, payload - %s", url, payload)
    response = urllib2.urlopen(req, json.dumps(payload).encode('utf-8'))
    logger.debug(json.dumps(payload).encode('utf-8'))
    responseData = response.read()
    if isinstance(responseData, bytes):
        responseData = responseData.decode('utf8')
    responseData = json.loads(responseData)
    return responseData


class scannerEngine():
    def __init__(self, sshPrefix=None):
        self.osInstanceClasses = self.getInstanceClasses()
        self.instance = self.__getInstance(sshPrefix)

    def getInstanceClasses(self):
        self.detectors = None
        members = set()
        for modPath, modName, isPkg in pkgutil.iter_modules(scanModules.__path__):
            #find all classed inherited from scanner.osDetect.ScannerInterface in all files
            members = members.union(inspect.getmembers(__import__('%s.%s' % ('scanModules',modName), fromlist=['scanModules']),
                                         lambda member:inspect.isclass(member)
                                                       and issubclass(member, scanModules.osDetect.ScannerInterface)
                                                       and member.__module__ == '%s.%s' % ('scanModules',modName)
                                                       and member != scanModules.osDetect.ScannerInterface))
        return members

    def getInstance(self):
        return self.instance

    def __getInstance(self,sshPrefix):
        inited = [instance[1](sshPrefix) for instance in self.osInstanceClasses]
        if not inited:
            raise Exception("No OS Detection classes found")
        osInstance = max(inited, key=lambda x:x.osDetectionWeight)
        if osInstance.osDetectionWeight:
            return osInstance

    def auditSystem(self, apiKey, agentId, systemInfo=None):
        instance = self.getInstance()
        installedPackages = instance.getPkg()
        if systemInfo:
            logger.warn("Host info - %s" % systemInfo)
        logger.warn("OS Name - %s, OS Version - %s" % (instance.osFamily, instance.osVersion))
        logger.warn("Total found packages: %s" % len(installedPackages))
        if not installedPackages:
            return instance
        # Get vulnerability information
        payload = {'apiKey':apiKey,
                   'agentId':agentId,
                   'os':instance.osFamily,
                   'version':instance.osVersion,
                   'package':installedPackages}
        url = VULNERS_LINKS.get('pkgChecker')
        response = sendHttpRequest(url, payload)
        resultCode = response.get("result")
        if resultCode != "OK":
            logger.error("Error - %s" % response.get('data').get('error'))
        else:
            vulnsFound = response.get('data').get('vulnerabilities')
            if not vulnsFound:
                logger.warn("No vulnerabilities found")
            else:
                payload = {'id':vulnsFound}
                allVulnsInfo = sendHttpRequest(VULNERS_LINKS['bulletin'], payload)
                vulnInfoFound = allVulnsInfo['result'] == 'OK'
                logger.warn("Vulnerable packages:")
                for package in response['data']['packages']:
                    logger.debug(" "*4 + package)
                    packageVulns = []
                    for vulns in response['data']['packages'][package]:
                        if vulnInfoFound:
                            vulnInfo = "{id} - '{title}', cvss.score - {score}".format(id=vulns,
                                                                                       title=allVulnsInfo['data']['documents'][vulns]['title'],
                                                                                       score=allVulnsInfo['data']['documents'][vulns]['cvss']['score'])
                            packageVulns.append((vulnInfo,allVulnsInfo['data']['documents'][vulns]['cvss']['score']))
                        else:
                            packageVulns.append((vulns,0))
                    packageVulns = sorted(packageVulns, key=lambda x:x[1])
                    packageVulns = [" "*8 + x[0] for x in packageVulns]
                    logger.debug("\n".join(packageVulns))

        return instance

    def scan(self, checkDocker = False):
        #scan host machine
        hostInstance = self.auditSystem(systemInfo="Host machine")

class agentEngine():
    def __init__(self):
        self.config = configReader()
        self.host = scannerEngine()

    def register(self):
        apiKey = self.getApiKey()
        if not apiKey:
            logger.error("No APi key found, exiting")
            sys.exit()

        data = sendHttpRequest(VULNERS_LINKS['agentRegister'],{"apiKey":apiKey,"agentType":AGENT_TYPE,"agentVersion":AGENT_VERSION})
        if data.get("result") != "OK":
            logger.error("Error during agent registration  - %s" % data.get("data",{}).get("error"))
            sys.exit(1)

        agentId = data["data"]["agentId"]
        self.config.setItem("agent", "agent_id", agentId)
        return True

    def getHostName(self):
        fqdn = self.config.getItem("agent", "fqdn")
        if not fqdn:
            fqdn = self.host.getInstance().getHostName()
            self.config.setItem("agent", "fqdn", fqdn)
        return fqdn

    def getApiKey(self):
        return self.config.getItem("agent", "api_key")

    def getAgentId(self):
        return self.config.getItem("agent", "agent_id")

    def getIP(self):
        ipaddr = self.config.getItem("agent", "ipaddr")
        if not ipaddr:
            ipaddr = self.host.getInstance().getIP()
            self.config.setItem("agent", "ipaddr", ipaddr)
        return ipaddr


    def getOSInfo(self):
        return (self.host.getInstance().osFamily, self.host.getInstance().osVersion)


    def healthCheck(self):
        if not self.config.getItem("agent","agent_id"):
            self.register()


        payload={'apiKey':self.getApiKey(),
                 'agentId':self.getAgentId(),
                 'agentType':AGENT_TYPE,
                 'agentVersion':AGENT_VERSION,
                 'ipaddress':self.getIP(),
                 'fqdn':self.getHostName(),
                 'macaddress':"",
                 'OSName':self.getOSInfo()[0],
                 'OSVersion':self.getOSInfo()[1]}

        data = sendHttpRequest(VULNERS_LINKS['agentUpdate'],payload)
        if data["result"] != "OK":
            logger.error("Error while update agent - %s" % data.get("data",{}).get("error"))
            return False
        else:
            return True


    def main(self):
        if self.healthCheck():
            self.host.auditSystem(self.getApiKey(), self.getAgentId())


class configReader():
    def __init__(self):

        self.config_path = os.path.realpath(os.path.join(os.path.dirname(__file__),"conf/vulners.conf"))
        self.config = {"main":
                        {
                               "debug": "false",
                            "http_proxy": ""},
                       "agent":
                        {       "api_key": "",
                                   "api_host": "vulners.com",
                                   "agent_id": "",
                                       "fqdn": "",
                                     "ipaddr": ""}}
        self.parseConfig()

    def parseConfig(self):
        global HTTP_PROXY
        global API_HOST
        self.config_parser = ConfigParser()
        self.config_parser.readfp(open(self.config_path))

        for section in self.config.keys():
            if self.config_parser.has_section(section):
                section_items = self.config_parser.items(section)
                for k,v in section_items:
                    if v:
                        self.config[section][k] = v
        HTTP_PROXY = self.config["main"]["http_proxy"]
        API_HOST = self.config["agent"]["api_host"]
        DEBUG_ENABLE = self.config["main"]["debug"]
        if DEBUG_ENABLE.lower() == "true":
            logger.setLevel(logging.DEBUG)

    def getItem(self, section, key):
        return self.config[section].get(key)

    def setItem(self, section, key, value):
        self.config_parser.set(section, key, value)
        self.config[section][key] = value
        with open(self.config_path, 'wb') as conf:
            self.config_parser.write(conf)



if __name__ == "__main__":
    configInstance = configReader()
    configInstance.parseConfig()
    agent = agentEngine()
    agent.main()
