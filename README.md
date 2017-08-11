# Agent installation

## Configure repository

### For rhel-based linux:
Create file /etc/yum.repos.d/vulners.repo

For rhel6:

```
[vulners]
name=Vulners Agent
baseurl=https://repo.vulners.com/redhat/el6/
enabled=1
gpgcheck=0
```

For rhel7:
```
[vulners]
name=Vulners Agent
baseurl=https://repo.vulners.com/redhat/el7/
enabled=1
gpgcheck=0
```

### For debian-based linux:

First add vulners.com pubkey:
```
wget -O- https://repo.vulners.com/pubkey.txt | apt-key add -
```

After this create file /etc/apt/sources.list.d/vulners.list
```
deb http://repo.vulners.com/debian jessie main
```

## Install packet:

### RHEL
```yum install vulners-agent.noarch```

### Debian 
```apt-get update && apt-get install vulners-agent.noarch```

## Agent configuration
Now you should get api-key for agent registration. Log in to vulners.com, go to userinfo space https://vulners.com/userinfo. Then you should choose "apikey" section.
Choose "scan" in scope menu and click "Generate new key". You will get an api-key, which look like this:
**RGB9YPJG7CFAXP35PMDVYFFJPGZ9ZIRO1VGO9K9269B0K86K6XQQQR32O6007NUK**

This key you'll need to write into agent configuration. You should use only one api key for all your agents. Agent configuration is located in file  /opt/vulners/conf/vulners.conf
You should change parameter api_key in section agent. Here is example of config file:

```
[main]
debug = false
;http_proxy=http://192.168.1.1:8080

[agent]
api_host = 
ipaddr = 
fqdn =
agent_id = 
api_key = RGB9YPJG7CFAXP35PMDVYFFJPGZ9ZIRO1VGO9K9269B0K86K6XQQQR32O6007NUK
```

## Agent execution

During first run agent will automatically register with configured api_key and set agent_id in configuration file. You can check that parameter agent_id is not null

After this you may look at scanning results at https://vulners.com/audit

Agent is executed every 2 hours via crontask

## Advanced configuration

### http_proxy
If host doesn't have direct access to the Interney, you may use parameter http_proxy for defining http proxy.

### ipaddr, fqdn
For matching corresponding server in reporting, vulners agent detect local ip address and fqdn of the host during first run. This values are written to parameter ipaddr and fqdn. If you are aware of private data leakage, you are able to set your own values for these paramaters. In that case they won't be overwritten by agent and will be used as a main.
