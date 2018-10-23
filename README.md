# What if everything is down?

## Control Node Setup

1. Create a new [Ubuntu 18.04 LTS](http://releases.ubuntu.com/18.04/ubuntu-18.04.1-desktop-amd64.iso) VM, or use your existing one. These instructions should generally work on newer versions and other distros, but no promises.
2. Open the terminal and enter the following commands:
3. `sudo apt-get install ansible git-crypt`
4. `pip install linode-python`.
5. `git clone https://github.com/thundernest/thundernest-ansible.git`
6. `ansible-galaxy install geerlingguy.apache`
7. Get the `thundernest-ansible.key` from 1password, labeled `git-crypt key for thundernest-ansible`.
8. Get the `thundernest-infra` RSA key labeled `Linode ssh private key` from 1password. Copy it to ~/.ssh, `chmod 600 thundernest-infra` and `mv thundernest-infra id_rsa`.
9. `cd thundernest-ansible` and `git-crypt unlock thundernest-ansible.key`.
10. `cat files/secrets.sh` should produce readable output now, if the unlock was successful.
11. `source files/secrets.sh`.
12. Optional: If the Fremont Linode data center is completely down, change `linode_datacenter: 3` in `vars/conf.yml` to [one of the alternate data centers listed on the Linode website](https://www.linode.com/api/utility/avail.datacenters), such as '2'.
13. `ansible-playbook --extra-vars "server_hostname=control2 linode_plan=1" provision-server.yml`.
14. In `~/thundernest-ansible/hosts` change the `[control]` section to read:
```
[control]
control2.thunderbird.net
```
15. `ansible-playbook control-node.yml`
16. `scp ~/thundernest-ansible/thundernest-ansible.key ansibler@control2.thunderbird.net:~/thundernest-ansible`
17. `scp ~/.ssh/id_rsa ansibler@control2.thunderbird.net:~/.ssh`
18. `ssh ansibler@control2.thunderbird.net`
19. `cd thundernest-ansible && git-crypt unlock thundernest-ansible.key`

# Web Server Setup
The following instructions assume you are logged into the control node via ssh to `control.thunderbird.net`. You will need the key labeled **'Linode ssh private key'** from 1password. If the control node is down or broken, follow the "Control Node Setup" to replace it.
1. In `~/thundernest-ansible`: `source files/secrets.sh`
2. `python build_servers.py production web3 web4`
3. `python lino.py nodecreate web3 web4`

At this point everything should be functional. You can test the system by changing your /etc/hosts to point the thunderbird.net domains at the new load balancer IP, or like this, **using the LOAD BALANCER IP in place of 127.0.0.1**.

```bash
curl -v --header 'Host: mx.thunderbird.net' 'http://127.0.0.1/dns/mx/google.com'
curl -v --header 'Host: broker.thunderbird.net' -H 'Accept-Language: en-US' 'http://127.0.0.1/provider/list'
curl -v -L --header 'Host: live.thunderbird.net' -H 'Accept-Language: en-US' 'http://127.0.0.1/thunderbird/start'
curl -v -L --header 'Host: autoconfig.thunderbird.net' -H 'Accept-Language: en-US' 'http://127.0.0.1/v1.1'
```
I also encourage testing Thunderbird. If you change your /etc/hosts so that mx, broker, live, and autoconfig.thunderbird.net are pointed at the new load balancer, Thunderbird will attempt to use it for requests. You can test the Get a New Email function, test that the start page loads, etc.

Once you have confirmed all of this, you can follow the steps below to set your new load balancer and web servers live:

1. [Login to Linode](https://manager.linode.com/nodebalancers) and check the IP assigned to the newly created Load Balancer.
2. [Login to Cloudflare](https://www.cloudflare.com/a/login) DNS using the 1password login and set the `thunderbird.net` A record to the IP address of the load balancer.
3. www.thunderbird.net should now be reachable.

# What if the SSL certs are expired?

1. The SSL certs are stored in [thundernest-ansible/files](https://github.com/thundernest/thundernest-ansible/tree/master/files).
2. They are normally renewed automatically on the 21st of each month, and committed to the repository.
3. To renew them manually:
```bash
source ~/letsencrypt/bin/activate
source ~/thundernest-ansible/files/secrets.sh
cd ~/letsencrypt
./dehydrated --register --accept-terms
./dehydrated -c -t dns-01 -k 'hooks/cloudflare/hook.py'
deactivate
~/thundernest-ansible/files/updatecerts.sh
```

# Architecture
The web servers are set up as two(2) *webheads* behind a single(1) Linode load balancer. A *webhead* is a Linode VPS running CentOS 7 and Apache which is set up to serve the actual content. The load balancer assigns incoming connections to the webheads, and is a service provided by Linode. Administration and changes are made through a *control node* running on a fourth Linode VPS by using [Ansible](http://docs.ansible.com/ansible/intro_getting_started.html) scripts that automatically perform changes. No changes are ever made directly to the other servers by manual ssh commands, and the only reason to ssh directly to them is to troubleshoot or to verify changes were applied correctly.

Production hostnames are the following:

Control Node: `control.thunderbird.net`  
Webheads: `thunderbird1.thunderbird.net and thunderbird2.thunderbird.net`  
Load Balancer: `thunderbird.net` itself as well as additional domains using CNAMEs for any service running such as `live.thunderbird.net, mx.thunderbird.net, broker.thunderbird.net, www.thunderbird.net` etc.

A set of web servers and a load balancer are entirely independent, and which set of servers is being used as 'production' depends solely on the IP assigned to the `thunderbird.net` A record in [Cloudflare](https://www.cloudflare.com/a/login) DNS.

The load balancer handles incoming connections first, whereas connections from the load balancer to the webheads are http, the load balancer needs SSL certs. You can generate these certs with the dehydrated script. If this is a brand new control node that hasn't been used before by anyone, the instructions below might prompt you to run `./dehydrated --register --accept-terms` before proceeding:
