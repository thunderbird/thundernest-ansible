import helpers.executor
import helpers.certs
import os

webhead_plan = 1

runcommands = [
        ['ansible-playbook','--extra-vars', 'server_hostname=web3 linode_plan={0}'.format(webhead_plan), 'provision-server.yml'],
        ['ansible-playbook','--extra-vars', 'server_hostname=web4 linode_plan={0}'.format(webhead_plan), 'provision-server.yml'],
        ['ansible-playbook','-i', 'web3.thunderbird.net,web4.thunderbird.net',
         '--extra-vars', 'var_hosts=all', 'setup-webheads.yml'],

]

helpers.executor.run(runcommands, env=os.environ.copy())
