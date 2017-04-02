import helpers.executor
import helpers.certs
import os
import sys

try:
	action = sys.argv[1]
except IndexError:
	sys.exit('You must enter which cluster to build: production, test, or stage')

if action == 'test':
	webhead_plan = 1
	webhead_names = ['webtest1', 'webtest2']
	runcommands = [
	        ['ansible-playbook','--extra-vars', 'server_hostname={0} linode_plan={1}'.format(webhead_names[0], webhead_plan), 'provision-server.yml'],
	        ['ansible-playbook','--extra-vars', 'server_hostname={0} linode_plan={1}'.format(webhead_names[1], webhead_plan), 'provision-server.yml'],
	        ['ansible-playbook','-i', '{0}.thunderbird.net,{1}.thunderbird.net'.format(webhead_names[0], webhead_names[1]),
	         '--extra-vars', 'var_hosts=all', 'setup-webheads.yml'],
		]

if action == 'quicktest':
	# Just build one web server to test that process quickly.
	webhead_plan = 1
	webhead_names = ['tbwebtest']
	runcommands = [
	        ['ansible-playbook','--extra-vars', 'server_hostname={0} linode_plan={1}'.format(webhead_names[0], webhead_plan), 'provision-server.yml'],
	        ['ansible-playbook','-i', '{0}.thunderbird.net,'.format(webhead_names[0]),
	         '--extra-vars', 'var_hosts=all', 'setup-webheads.yml'],
		]
	
if action == 'production':
	if len(sys.argv) < 4:
		sys.exit('You must enter two names for the webheads in addition to the production action')
	webhead_names = []
	webhead_names.append(sys.argv[2])
	webhead_names.append(sys.argv[3])
	webhead_plan = 4
	runcommands = [
	        ['ansible-playbook','--extra-vars', 'server_hostname={0} linode_plan={1}'.format(webhead_names[0], webhead_plan), 'provision-server.yml'],
	        ['ansible-playbook','--extra-vars', 'server_hostname={0} linode_plan={1}'.format(webhead_names[1], webhead_plan), 'provision-server.yml'],
	        ['ansible-playbook','-i', '{0}.thunderbird.net,{1}.thunderbird.net'.format(webhead_names[0], webhead_names[1]),
	         '--extra-vars', 'var_hosts=all', 'setup-webheads.yml'],
		]

if action == 'stage':
	webhead_plan = 1
	webhead_names = ['webstage1', 'webstage2']
	runcommands = [
	        ['ansible-playbook','--extra-vars', 'server_hostname={0} linode_plan={1}'.format(webhead_names[0], webhead_plan), 'provision-server.yml'],
	        ['ansible-playbook','--extra-vars', 'server_hostname={0} linode_plan={1}'.format(webhead_names[1], webhead_plan), 'provision-server.yml'],
	        ['ansible-playbook','-i', '{0}.thunderbird.net,{1}.thunderbird.net'.format(webhead_names[0], webhead_names[1]),
	         '--extra-vars', 'var_hosts=all branch=master', 'setup-webheads.yml'],
		]



helpers.executor.run(runcommands, env=os.environ.copy())
