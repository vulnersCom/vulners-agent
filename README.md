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
gpgcheck=1
```

For rhel7:
```
[vulners]
name=Vulners Agent
baseurl=https://repo.vulners.com/redhat/el7/
enabled=1
gpgcheck=1
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
```yum install vulners-agent```

### Debian 
```apt-get update && apt-get install vulners-agent```

## Agent configuration
Now you should get api-key for agent registration. Log in to vulners.com, go to userinfo space https://vulners.com/userinfo. Then you should choose "apikey" section.
Choose "scan" in scope menu and click "Generate new key". You will get an api-key, which looks like this:
**RGB9YPJG7CFAXP35PMDVYFFJPGZ9ZIRO1VGO9K9269B0K86K6XQQQR32O6007NUK**

You'll need to write this key into agent configuration. You should use only one api key for all your agents. Agent configuration is located in file /etc/vulners/vulners_agent.conf
Change parameter api_key in section agent. Here is example of config file:

```
[DEFAULT]
api_key = RGB9YPJG7CFAXP35PMDVYFFJPGZ9ZIRO1VGO9K9269B0K86K6XQQQR32O6007NUK
```

## Agent execution

During first run agent will automatically register with configured api_key 

After this you may look at agent status and scanning results at https://vulners.com/audit

## Advanced configuration

Using /etc/vulners/vulners_agent.conf you can override part of the identification parameters.

```
[DEFAULT]
api_key = RGB9YPJG7CFAXP35PMDVYFFJPGZ9ZIRO1VGO9K9269B0K86K6XQQQR32O6007NUK

[Ticker]
ip_address = 10.0.0.1
fqdn = my.host.example.com
mac_address = 00:01:02:03:04:06

```
