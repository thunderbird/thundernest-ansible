
domain = 'sancus.ca'
tests = [
    {
        'display_name': 'http-mx service',
        'website': 'https://mx.{0}/dns/mx/google.com'.format(domain),
        "monitor_id": "217222000000026003",
    },
    {
        'display_name': 'broker get-email-account service',
        'website': 'https://broker.{0}/provider/list'.format(domain),
        "monitor_id": "217222000000025127",
    },
    {
        'display_name': 'autoconfig',
        'website': 'https://autoconfig.{0}/v1.1/'.format(domain),
        "monitor_id": "217222000000028003",
    },
]

live_tests = [
    {
        'display_name': 'live start redirect',
        'website': 'https://live.{0}/thunderbird/start'.format(domain),
        "monitor_id": "217222000000028013",
    },
    {
        'display_name': 'live firstrun redirect',
        'website': 'https://live.{0}/thunderbird/firstrun'.format(domain),
        "monitor_id": "217222000000030003",
    },
]

general_settings = {
        'type': 'URL',
        'check_frequency': '1',
        'timeout': '15',
        'location_profile_id': '217222000000025021',
        'notification_profile_id': '217222000000025066',
        'threshold_profile_id': '217222000000025063',
        'user_group_ids': ['217222000000025003'],
        'http_method': 'G',
}

for test in tests:
    test.update(general_settings)
for test in live_tests:
    test.update(general_settings)
