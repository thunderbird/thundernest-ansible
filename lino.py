
import argparse
import linode.api
import json
import requests
import sys
import yaml

from distutils.util import strtobool

# For the API key
secrets_file = 'vars/secrets.yml'
vars_file = 'vars/conf.yml'

# cloudflare settings
cloudflare_zone_identifier = '10eb4a11ab885340bd57de0c72a4ee55'
cloudflare_url = 'https://api.cloudflare.com/client/v4'

# SSL key/certs for the load balancer
key_file = '../dehydrated/certs/sancus.ca/privkey.pem'
fullchain_file = '../dehydrated/certs/sancus.ca/fullchain.pem'

# payment_term should always be 1, artifact of bad linode-python code
payment_term = 1

with open(key_file, 'r') as f:
    sslkey = f.read()
with open(fullchain_file, 'r') as f:
    sslcert = f.read()
with open(secrets_file, 'r') as f:
    doc = yaml.load(f)
    api_key = doc['linode_api_key']
    cloudflare_api_key = doc['cloudflare_api_key']
    cloudflare_email = doc['cloudflare_email']
with open(vars_file, 'r') as f:
    doc = yaml.load(f)
    server_domain = doc['server_domain']
    datacenter = doc['linode_datacenter']

api = linode.api.Api(api_key)
cloudflare_headers = {'X-Auth-Email': cloudflare_email,
                      'X-Auth-Key': cloudflare_api_key,
                      'Content-Type': 'application/json'}


def nodebalancer_config(balancerid, **kwargs):
    # https://www.linode.com/api/nodebalancer/nodebalancer.config.create
    port = kwargs.get('port', 80)
    protocol = kwargs.get('protocol', 'http')
    algorithm = kwargs.get('algorithm', 'roundrobin')
    check = kwargs.get('check', 'http')
    check_path = kwargs.get('check_path', '/version.txt')
    stickiness = kwargs.get('stickiness', 'table')

    config = {
        'NodeBalancerID': balancerid,
        'Port': port,
        'Protocol': protocol,
        'Algorithm': algorithm,
        'check': check,
        'check_path': check_path,
        'stickiness': stickiness,
    }

    if protocol == 'https':
        config['Port'] = 443
        config['ssl_cert'] = sslcert
        config['ssl_key'] = sslkey
        config['cipher_suite'] = 'recommended'
    return config


def main():
    parser = argparse.ArgumentParser(
    description="""
    python lino.py listnodes (list linodes with their IPs)
    python lino.py delete thunder1, thunder2, ... (deletes linodes by label)
    python lino.py nodecreate thunder1, thunder2, ... (creates node balancer for labeled nodes)
    python lino.py reboot thunder1, thunder2, ...(reboots linodes by label)
    """, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('action', nargs='+')
    args = parser.parse_args()

    if args.action[0] == 'delete':
        # slice off the first argument since its the command itself
        delete(args.action[1:])
    elif args.action[0] == 'listnodes':
        listnodes()
    elif args.action[0] == 'nodecreate':
        nodebalancercreate(args.action[1:])
    elif args.action[0] == 'reboot':
        reboot(args.action[1:])
    else:
        sys.exit('No known action requested. Maybe you meant delete, listnodes, or nodecreate?')


def cf_get_identifier(hostname):
    # Get the identifier for an A record, takes the first one listed by cf
    identifier_url = "{0}/zones/{1}/dns_records".format(cloudflare_url, cloudflare_zone_identifier)
    response = requests.get(identifier_url, headers=cloudflare_headers)
    fullname = hostname + '.{0}'.format(server_domain)
    if response:
        data = json.loads(response.text)
        for record in data['result']:
            if record['name'] == fullname:
                return record['id']
        return False
    else:
        return False


def cf_delete_dns_record(record_id):
    # Delete cloudflare A record by identifier from cf_get_identifier
    delete_url = "{0}/zones/{1}/dns_records/{2}".format(cloudflare_url, cloudflare_zone_identifier, record_id)
    response = requests.delete(delete_url, headers=cloudflare_headers)
    if response:
        data = json.loads(response.text)
        if data['success']:
            return True
        else:
            return False
    else:
        return False


def reboot(labels):
    if not labels:
        sys.exit('You must enter the labels to reboot')

    vpsids = {}
    toreboot = {}

    for vps in api.linode_list():
        vpsids[vps['LABEL']] = vps['LINODEID']
    for label in labels:
        for k, v in vpsids.iteritems():
            if label in k:
                toreboot[label] = v
    for l in toreboot.values():
        r = api.linode_reboot(LinodeID=l)
        print r


def nodehasprivateip(linodeid):
    for ip in api.linode_ip_list():
        if not ip['ISPUBLIC'] and ip['LINODEID'] == linodeid:
            return ip['IPADDRESS']

    r = api.linode_ip_addprivate(LinodeID=linodeid)
    a = api.linode_reboot(LinodeID=linodeid)
    print a
    return r['IPADDRESS']


def nodebalancercreate(labels):
    if not labels:
        sys.exit('You must enter the labels of the webheads.')
    vpsids = {}
    toadd = {}
    webheads = {}
    configs = []

    for vps in api.linode_list():
        vpsids[vps['LABEL']] = vps['LINODEID']
    for label in labels:
        for k, v in vpsids.iteritems():
            if label in k:
                toadd[label] = v
    for k, v in toadd.iteritems():
        webheads[k] = nodehasprivateip(v)

    r = api.nodebalancer_create(DatacenterID=datacenter, PaymentTerm=payment_term)

    if r['NodeBalancerID']:
        a = api.nodebalancer_config_create(**nodebalancer_config(r['NodeBalancerID']))
    else:
        sys.exit('No node balancer id after creation attempt, something failed majorly.')

    if a['ConfigID']:
        configs.append(a['ConfigID'])
    else:
        sys.exit('Failed trying to create HTTP config for node balancer.')

    a = api.nodebalancer_config_create(**nodebalancer_config(r['NodeBalancerID'], protocol='https'))
    if a['ConfigID']:
        configs.append(a['ConfigID'])
    else:
        sys.exit('Failed trying to create HTTPS (SSL) config for node balancer.')

    # Add the nodes to the load balancer
    for l, ip in webheads.iteritems():
        for cid in configs:
            a = api.nodebalancer_node_create(ConfigID=cid, Label=l, Address='{0}:80'.format(ip))
            if not a['NodeID']:
                sys.exit('Failed trying to add a node to the load balancer ID: {0}'.format(cid))

    print "Node Balancer configs created:{0}".format(configs)


def listnodes():
    vpslist = {}
    for ips in api.linode_ip_list():
        linodeid = ips['LINODEID']
        label = api.linode_list(LINODEID=linodeid)[0]['LABEL']
        ip = ips['IPADDRESS']
        public = ips['ISPUBLIC']
        if not vpslist.get(label):
            vpslist[label] = {}
            vpslist[label][linodeid] = []
            vpslist[label][linodeid].append(dict(ISPUBLIC=public, IPADDRESS=ip))
        else:
            vpslist[label][linodeid].append(dict(ISPUBLIC=public, IPADDRESS=ip))

    for key, value in vpslist.iteritems():
        vpslist[key]
        print '{0}: {1}'.format(key, value)


def delete(labels):
    vpsids = {}
    todelete = {}  # dict label:linodeid of the nodes to be deleted

    for vps in api.linode_list():
        vpsids[vps['LABEL']] = vps['LINODEID']
    for label in labels:
        for key, value in vpsids.iteritems():
            if label in key:
                todelete[label] = value
    if todelete:
        print todelete
        if prompt('Are you sure you want to delete the above instances?'):
            for key, value in todelete.iteritems():
                r = api.linode_delete(LINODEID=value, skipChecks=1)
                if r:
                    print r
                    if cf_delete_dns_record(cf_get_identifier(key)):
                        print "{0} DNS record deleted.".format(key)
    else:
        print "Can't delete, no linodes matched: " + " ".join(labels[1:])


def prompt(query):
    sys.stdout.write('%s [y/n]: ' % query)
    val = raw_input()
    try:
        ret = strtobool(val)
    except ValueError:
        sys.stdout.write('Please answer with a y/n\n')
        return prompt(query)
    return ret


if __name__ == '__main__':
    main()
