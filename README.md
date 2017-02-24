# Server Setup Instructions
The following instructions assume you are logged into the control node. Login instructions are attached as
a **note to the private key in 1password**. All other login information for any service mentioned below is also in 1password.

```bash
cd ~/thundernest-ansible
ansible-playbook --extra-vars "server_hostname=thunderbird3 linode_plan=4" provision-server.yml
ansible-playbook --extra-vars "server_hostname=thunderbird4 linode_plan=4" provision-server.yml
```
You can make more webheads if you want, or use different hostnames. I use plan 4 for this, which is the $40/mo 4-core plan.

Verify DNS was added in [Cloudflare](https://www.cloudflare.com/a/login), and add **thunderbird3.thunderbird.net** and **thunderbird4.thunderbird.net** to the file named `~/thundernest-ansible/hosts` under [webheads]:

```yml
[webheads]
thunderbird3.sancus.ca
thunderbird4.sancus.ca
```
Set up the webheads:
```bash
ansible-playbook setup-webheads.yml
```
Now generate the SSL certs for the load balancer:

```bash
source ~/letsencrypt/bin/activate
cd ~/letsencrypt
./dehydrated -c -t dns-01 -k 'hooks/cloudflare/hook.py'
deactivate
```
Build the load balancer:

```bash
cd ~/thundernest-ansible
python lino.py thunderbird3 thunderbird4
```
This should create a node balancer in linode. It should have an https config and a http config, with 2 nodes on each(or more, if you created more).

At this point everything should be functional. You can test the system by changing your /etc/hosts to point the *.thunderbird.net domains at the new load balancer IP, or like this, **using the LOAD BALANCER IP in place of 127.0.0.1**.

```bash
curl -v --header 'Host: mx.thunderbird.net' 'http://127.0.0.1/dns/mx/google.com'
curl -v --header 'Host: broker.thunderbird.net' -H 'Accept-Language: en-US' 'http://127.0.0.1/provider/list'
curl -v -L --header 'Host: live.thunderbird.net' -H 'Accept-Language: en-US' 'http://127.0.0.1/thunderbird/start'
curl -v -L --header 'Host: autoconfig.thunderbird.net' -H 'Accept-Language: en-US' 'http://127.0.0.1/v1.1'
```
I also encourage testing Thunderbird. If you change your /etc/hosts so that mx, broker, live, and autoconfig.thunderbird.net are pointed at the new load balancer, Thunderbird will attempt to use it for requests. You can test the Get a New Email function, test that the start page loads, etc.

Once you have confirmed all of this, you can finally turn everything on by going into Cloudflare DNS setup, and setting the A record for live.thunderbird.net to the new load balancer Public IP. You can find that in the Linode web ui or by running `python lino.py listnodes`. No other records need be changed, as they are CNAMEd to live.thunderbird.net.
