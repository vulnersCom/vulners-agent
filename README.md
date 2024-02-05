# Vulners agent

![Vulners Agent](img/vulners_logo.png)

Vulners agent is an open source solution, which provides vulnerability assessment for Linux-based and Windows operating systems. The agent performs scans with minimum execution commands and, as a result, achieves extremely fast scanning speed. You will need the **Python 3** to install the agent.

The agent gathers information about your operating system, its version, and any installed packages. This information is then sent to Vulners API to find out which software is vulnerable. You can check how it works in [manual mode](https://vulners.com/audit) to evaluate the results.

![Vulners Audit IP Summary](img/audit_ipsummary.png)

## Installation for Linux-based operating systems

### Configure a repository for RHEL-based Linux:

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

### Configure a repository for Debian-based Linux:

First, add vulners.com pubkey:
```
wget -O- https://repo.vulners.com/pubkey.txt | apt-key add -
```

Then, create file **/etc/apt/sources.list.d/vulners.list**
```
deb http://repo.vulners.com/debian focal main
```

### Install packet:

#### RHEL
```yum install vulners-agent```

#### Debian
```apt-get update && apt-get install vulners-agent```

### Source code (NOT recommended)
You could clone the source code of a package and perform scans using Python. According to best practices, this should be done in a virtual environment:

* install poetry as it's described on official website - https://python-poetry.org/docs/
* install requirements ```poetry install --no-root```,
* configure the agent as described below
* run ```poetry run ./application.py --app Scanner```.

## Configuration for Linux-based operating systems
Now, you have to generate an API key to register the agent. [Log in](https://vulners.com/userinfo) to Vulners, go to the userinfo space and click on the API KEYS tab. In the "Scope" field, select "scan", click SAVE and then copy the generated key. The result should look something like this:

**RGB9YPJG7CFAXP35PMDVYFFJPGZ9ZIRO1VGO9K9269B0K86K6XQQQR32O6007NUK**

Now, you can embed the generated key into the agent. The agent configuration file is located at /etc/vulners/vulners_agent.conf.

Example of the config file:

```
[DEFAULT]
api_key = RGB9YPJG7CFAXP35PMDVYFFJPGZ9ZIRO1VGO9K9269B0K86K6XQQQR32O6007NUK
```
You can use one API key for all your agents.

### Execution

During the first run, the agent will be automatically registered with the configured API key.

Perform a system scan by running ```vulners-agent --app Scanner```.

Once finished, you can view agent status and scan results in the [Audit](https://vulners.com/linux-scanner/audit) section of your personal account. 

### Advanced configuration

Using /etc/vulners/vulners_agent.conf you can override part of the identification parameters.

```
[DEFAULT]
api_key = RGB9YPJG7CFAXP35PMDVYFFJPGZ9ZIRO1VGO9K9269B0K86K6XQQQR32O6007NUK

[Ticker]
ip_address = 10.0.0.1
fqdn = my.host.example.com
mac_address = 00:01:02:03:04:06
interval = 3h30m
tags = tag1,tag2 ;comma separated user defined values
```

## Installation and configuration for Windows
Run VulnersAgentInstaller_v2.2.0.msi and follow wizard.

Generate API-key to register the agent and paste it during the configuration step. 
If necessary, you can set an alternate Vulners host or Vulners proxy address. You can also set agent identification parameters, such as IP address and FQDN. You will see these parameters in the Dashboard. 

<img src="img/configuration.png" alt="drawing" width="450"/>

Press Next and finish installation. Scanning process will be started automatically.

To run installer silently use following arguments
- APIKEY (required)
- INSTALLDIR
- HOST
- IP
- FQDN
- MAC

The installation process will create a scheduled task that performs the scan and a configuration file. You can use the Windows Task Scheduler console to adjust the scan interval. The configuration and logs are located in the Program Data folder. 