#!/usr/bin/python

# ./dehydrated -c -t http-01 -k '../thundernest-ansible/dehydrated/hook.py'

import os
import sys
import subprocess
os.chdir('../thundernest-ansible')

if sys.argv[1] == 'deploy_challenge' or sys.argv[1] == 'clean_challenge':
	filename = sys.argv[3]
	filedata = sys.argv[4]
else:
	sys.exit()

deploy_dir = '/var/www/dehydrated/' # trailing slash mandatory
deploy = 'ansible webheads -m shell -a \'echo \"{0}\" >> {1}{2}\''.format(filedata, deploy_dir, filename)
clean= 'ansible webheads -m shell -a "rm -rf {0}{1}"'.format(deploy_dir, filename)

if sys.argv[1] == 'deploy_challenge':
	out = subprocess.check_output(deploy, stderr=subprocess.STDOUT, shell=True)
	print out

if sys.argv[1] == 'clean_challenge':
	out = subprocess.check_output(clean, stderr=subprocess.STDOUT, shell=True)
	print out
