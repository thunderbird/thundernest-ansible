import requests
import health_tests
import m_login
import json

url = 'https://www.site24x7.com/api/monitors'
headers = {'Authorization': m_login.api_key, 'Accept': 'application/json; version=2.0',
           'Content-Type': 'application/json;charset=UTF-8'}


def update_tests(tests):
    for payload in tests:
        payload = json.dumps(payload)

        r = requests.post(url, payload, headers=headers)
        print r.text


update_tests(health_tests.tests)
# update_tests(health_tests.live_tests)
