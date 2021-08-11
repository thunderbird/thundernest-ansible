# Configure Kinto in AWS

Prereqs:
* Your own AWS credentials need to be in the environent:
* * `export AWS_ACCESS_KEY_ID='AK123'`
* * `export AWS_SECRET_ACCESS_KEY='abc123'`
* The secrets file must be loaded:
* * `source ../files/secrets.sh`
* `virtualenv -p python3 py3`
* `source py3/bin/activate`
* `pip install ansible boto boto3 botocore`
* `ansible-galaxy collection install amazon.aws`
* `ansible-galaxy collection install community.aws`
* `ansible-galaxy install geerlingguy.apache`

To run:
* `source py3/bin/activate` if you aren't already in the virtualenv
* `ansible-playbook --extra-vars "prodenv=stage" kinto-setup.yml`
* set prodenv=prod to run it on the production servers

To see a list of our AWS inventory, run the following:
* `ansible-inventory --graph`
