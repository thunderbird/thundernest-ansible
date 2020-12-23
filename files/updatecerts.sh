#!/bin/bash

exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>~/thundernest-ansible/ssl-refresh-log 2>&1

source ~/letsencrypt/bin/activate
source ~/thundernest-ansible/files/secrets.sh
source ~/amo-ops/env/secrets.sh
cd ~/dehydrated && ./dehydrated --algo rsa --preferred-chain "DST Root CA X3" --force -c -t dns-01 -k 'hooks/cloudflare/hook.py'
cd ~/thundernest-ansible
cp ~/dehydrated/certs/thunderbird.net/{cert,chain,fullchain,privkey}.pem files
ansible-playbook plays/refresh-ssl-certs.yml
ansible-playbook --extra-vars="var_hosts=webheads" plays/refresh-ssl-certs.yml
aws acm import-certificate --region us-west-2 --certificate file://~/thundernest-ansible/files/cert.pem --private-key file://~/thundernest-ansible/files/privkey.pem --certificate-chain file://~/thundernest-ansible/files/chain.pem --certificate-arn arn:aws:acm:us-west-2:768512802988:certificate/2cff184f-31a3-4e9e-b478-eff82076f06f
aws acm import-certificate --region us-east-1 --certificate file://~/thundernest-ansible/files/cert.pem --private-key file://~/thundernest-ansible/files/privkey.pem --certificate-chain file://~/thundernest-ansible/files/chain.pem --certificate-arn arn:aws:acm:us-east-1:768512802988:certificate/4ebbc853-6675-4f28-bc7c-12977101c275

