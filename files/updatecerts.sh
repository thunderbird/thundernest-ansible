#!/bin/bash

source ~/letsencrypt/bin/activate
source ~/thundernest-ansible/files/secrets.sh
cd ~/dehydrated && ./dehydrated --force -c -t dns-01 -k 'hooks/cloudflare/hook.py'
cd ~/thundernest-ansible
cp ~/dehydrated/certs/thunderbird.net/{cert,chain,fullchain,privkey}.pem files
ansible-playbook --extra-vars="var_hosts=stage" plays/refresh-ssl-certs.yml
