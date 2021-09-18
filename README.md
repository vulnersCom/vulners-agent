# Vulners Agent

![Vulners Agent](img/vulners_logo.png)

Vulners Agent is an open-source agent, which provides vulnerability assessment for linux-based systems. Due to a minimum number of commands he agent solution performs extremely fast scanning. The Agent is developed with Python and uses OS environment variables to detect any used Python version.

The Agent gathers information about operating system, it's/its version and installed packages. These/this information is sent to the vulners.com API and results can be viewed via [vulners.com audit result](https://vulners.com/audit)

![Vulners Audit IP Summary](img/audit_ipsummary.png)

# Agent installation

## Configure repository

### For rhel-based linux:

Create file **/etc/yum.repos.d/vulners.repo**

For rhel6:

```
[vulners]
name=Vulners Agent
baseurl=https://repo.vulners.com/redhat/el6/
enabled=1
gpgcheck=1
gpgkey=https://repo.vulners.com/pubkey.txt
```

For rhel7:
```
[vulners]
name=Vulners Agent
baseurl=https://repo.vulners.com/redhat/el7/
enabled=1
gpgcheck=1
gpgkey=https://repo.vulners.com/pubkey.txt
```

### For debian-based linux:

First add vulners.com pubkey:
```
wget -O- https://repo.vulners.com/pubkey.txt | apt-key add -
```

After this create file **/etc/apt/sources.list.d/vulners.list**
```
deb http://repo.vulners.com/debian jessie main
```

## Install packet:

### RHEL
```yum install vulners-agent```

### Debian
```apt-get update && apt-get install vulners-agent```

## Agent configuration
For agent registration get an api-key. At first, log in to vulners.com and go to [userinfo space] (https://vulners.com/userinfo). Then select the "apikey" section.
Select "scan" in the scope menu and click "Generate a new key". You will get an api-key, which looks like this:
**RGB9YPJG7CFAXP35PMDVYFFJPGZ9ZIRO1VGO9K9269B0K86K6XQQQR32O6007NUK**

You'll need to write this key into agent configuration. You should use only one api key for all your agents. Agent configuration is located in the following file /etc/vulners/vulners_agent.conf
Change the api_key parameter in the agent section. Here is an example of a config file:

```
[DEFAULT]
api_key = RGB9YPJG7CFAXP35PMDVYFFJPGZ9ZIRO1VGO9K9269B0K86K6XQQQR32O6007NUK
```

## Agent execution

During the first run the agent automatically registers with the configured api_key

After this the agent status and scanning results are available https://vulners.com/audit

## Advanced configuration

Using /etc/vulners/vulners_agent.conf you can override a part of the identification parameters.

```
[DEFAULT]
api_key = RGB9YPJG7CFAXP35PMDVYFFJPGZ9ZIRO1VGO9K9269B0K86K6XQQQR32O6007NUK

[Ticker]
ip_address = 10.0.0.1
fqdn = my.host.example.com
mac_address = 00:01:02:03:04:06

```
