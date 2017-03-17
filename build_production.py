import helpers.executor
import helpers.certs
import os

webhead_plan = 1

runcommands = [
        ['ansible-playbook','--extra-vars', 'server_hostname=thunderbird3 linode_plan={0}'.format(webhead_plan), 'provision-server.yml'],
        ['ansible-playbook','--extra-vars', 'server_hostname=thunderbird4 linode_plan={0}'.format(webhead_plan), 'provision-server.yml'],
        ['ansible-playbook','-i', 'thunderbird3.sancus.ca,thunderbird4.sancus.ca',
         '--extra-vars', 'var_hosts=all', 'setup-webheads.yml'],

]

helpers.executor.run(runcommands, env=os.environ.copy())
