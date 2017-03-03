# Architecture
The web servers are set up as two(2) *webheads* behind a single(1) Linode load balancer. A *webhead* is a Linode VPS running CentOS 7 and Apache which is set up to serve the actual content. The load balancer assigns incoming connections to the webheads, and is a service provided by Linode. Administration and changes are made through a *control node* running on a fourth Linode VPS by using [Ansible](http://docs.ansible.com/ansible/intro_getting_started.html) scripts that automatically perform changes. No changes are ever made directly to the other servers by manual ssh commands, and the only reason to ssh directly to them is to troubleshoot or to verify changes were applied correctly.

# Server Setup Instructions
The following instructions assume you are logged into the control node via ssh to `control.thunderbird.net`. You will need the key labeled **'Linode ssh private key'** from 1password. If there is no existing control node running for some reason instructions to build one are below. All other login information for any service mentioned below is also in 1password.

You can run these setup instructions and create additional servers without interfering with the production setup. Hostnames you provide will be used for your new setup, so the below instructions use example hostnames that are not used by the production setup. The production setup uses the following:

Control Node: `control.thunderbird.net`  
Webheads: `thunderbird1.thunderbird.net and thunderbird2.thunderbird.net`  
Load Balancer: `thunderbird.net` itself as well as additional domains using CNAMEs for any service running such as `live.thunderbird.net, mx.thunderbird.net, broker.thunderbird.net, www.thunderbird.net` etc.

The production setup is entirely separate, and which setup is being used as 'production' depends solely on the IP assigned to the thunderbird.net DNS A record.

First, create some linodes to use as webheads.

```bash
cd ~/thundernest-ansible
ansible-playbook --extra-vars "server_hostname=thunderbird3 linode_plan=4" provision-server.yml
ansible-playbook --extra-vars "server_hostname=thunderbird4 linode_plan=4" provision-server.yml
```
You can make more webheads if you want, or use different hostnames. I use plan 4 for this, which is the $40/mo 4-core plan.

Verify DNS A records for thunderbird3 and thunderbird4 were added in [Cloudflare](https://www.cloudflare.com/a/login) -- the ansible script should do this automatically. You will need to  add **thunderbird3.thunderbird.net** and **thunderbird4.thunderbird.net** to the file named `~/thundernest-ansible/hosts` under [webheads], so that ansible knows what servers you want to change when you run the rest of the setup instructions. It defaults to running all commands on the servers listed in the hosts file under [webheads]:

```yml
[webheads]
thunderbird3.thunderbird.net
thunderbird4.thunderbird.net
```
Running the following command will perform all necessary setup on the webheads:
```bash
ansible-playbook setup-webheads.yml
```
The load balancer handles incoming connections first, whereas connections from the load balancer to the webheads are http, the load balancer needs SSL certs. You can generate these certs with the dehydrated script. If this is a brand new control node that hasn't been used before by anyone, the instructions below might prompt you to run `./dehydrated --register --accept-terms` before proceeding:

```bash
source ~/letsencrypt/bin/activate
export CF_EMAIL='theemailfrom vars/secrets.yml'
export CF_KEY='thekeyfrom vars/secrets.yml'
cd ~/letsencrypt
./dehydrated -c -t dns-01 -k 'hooks/cloudflare/hook.py'
deactivate
```
Build the load balancer:

```bash
cd ~/thundernest-ansible
python lino.py thunderbird3 thunderbird4
```
This should create a "node balancer"(which is their name for their proprietary load balancer service) in linode. It should have an https config and a http config, with 2 nodes on each(or more, if you created more).

At this point everything should be functional. You can test the system by changing your /etc/hosts to point the thunderbird.net domains at the new load balancer IP, or like this, **using the LOAD BALANCER IP in place of 127.0.0.1**.

```bash
curl -v --header 'Host: mx.thunderbird.net' 'http://127.0.0.1/dns/mx/google.com'
curl -v --header 'Host: broker.thunderbird.net' -H 'Accept-Language: en-US' 'http://127.0.0.1/provider/list'
curl -v -L --header 'Host: live.thunderbird.net' -H 'Accept-Language: en-US' 'http://127.0.0.1/thunderbird/start'
curl -v -L --header 'Host: autoconfig.thunderbird.net' -H 'Accept-Language: en-US' 'http://127.0.0.1/v1.1'
```
I also encourage testing Thunderbird. If you change your /etc/hosts so that mx, broker, live, and autoconfig.thunderbird.net are pointed at the new load balancer, Thunderbird will attempt to use it for requests. You can test the Get a New Email function, test that the start page loads, etc.

Once you have confirmed all of this, you can finally **turn everything on by going into Cloudflare DNS setup, and setting the A record for live.thunderbird.net to the new load balancer Public IP**. You can find that in the Linode web ui or by running `python lino.py listnodes`. No other records need be changed, as they are CNAMEd to live.thunderbird.net.

## Control/Admin Node Build Instructions

These instructions will produce a brand new control node, which can be used to generate a new load balancer and new webheads. This should only ever be necessary if something catastrophic happened to the existing control node, which is typically at `control.thunderbird.net`. You will need ansible installed on a local VM or your machine, and you will also need git-crypt to unlock the password files. The key is in 1password, of course.  Ansible and git-crypt are available as packages on Ubuntu 16.04LTS and better.

Example:
`apt-get install ansible git-crypt`

clone the ansible repo locally:
`git clone https://github.com/thundernest/thundernest-ansible.git`

**Copy the thundernest-ansible.key into the folder from 1password.**

```bash
cd thundernest-ansible
git-crypt unlock thundernest-ansible.key
cat vars/secrets.yml
```

Verify that the passwords are decrypted properly.

Provision a linode. The cheapest plan is more than sufficient for this.

`ansible-playbook --extra-vars "server_hostname=control1 linode_plan=1" provision-server.yml`

Add control to the `~/thundernest-ansible/hosts` file:
```
[control]
control1.thunderbird.net
```
Now install everything necessary:

`ansible-playbook control-node.yml`

You can now ssh into ansibler@control1 -- You can remove ansible and its associated files from your local VM, it is no longer needed. **You will also need to git-crypt unlock thundernest-ansible to use this control node**, following the same procedure as on your local VM.

From here you can proceed to webhead setup or work on the servers.
