# Deployment scripts for addons.thunderbird.net

1. `source ~/thundernest-ansible/files/secrets.sh ; cd ~/thundernest-ansible/addons/playbooks`
2. `ansible-playbook --extra-vars "@../env/test-web.yml" deploy-instance.yml`
