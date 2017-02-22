import requests
import statuscake_tests
import statuscake_login

url = 'https://app.statuscake.com/API/Tests/Update'
headers = {'Username': statuscake_login.username, 'API': statuscake_login.api_key}

def update_tests(tests):
	for payload in tests:
		r = requests.put(url, payload, headers=headers)
		print "Test {0}: {1}".format(payload['WebsiteName'], r.text)

update_tests(statuscake_tests.tests)
update_tests(statuscake_tests.live_tests)
