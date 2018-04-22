#!/bin/bash

exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>~/thundernest-ansible/ssl-refresh-log 2>&1

source ~/letsencrypt/bin/activate
source ~/thundernest-ansible/files/secrets.sh
cd ~/dehydrated && ./dehydrated --force -c -t dns-01 -k 'hooks/cloudflare/hook.py'
cd ~/thundernest-ansible
cp ~/dehydrated/certs/thunderbird.net/{cert,chain,fullchain,privkey}.pem files
ansible-playbook plays/refresh-ssl-certs.yml
ansible-playbook --extra-vars="var_hosts=webheads" plays/refresh-ssl-certs.yml
