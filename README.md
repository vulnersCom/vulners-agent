# Agent installation

## Configure repository

### For rhel-based linux:
Create file /etc/yum.repos.d/vulners.repo

[vulners]
name=Vulners Agent
baseurl=https://repo.vulners.com/redhat/el6/
enabled=1
gpgcheck=0
