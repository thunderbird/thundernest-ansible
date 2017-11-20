source ~/letsencrypt/bin/activate
source ~/thundernest-ansible/files/secrets.sh
cd ~/letsencrypt && ./dehydrated --force -c -t dns-01 -k 'hooks/cloudflare/hook.py'

