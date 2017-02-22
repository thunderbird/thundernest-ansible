# To create new tests, do not pass TestID
domain = 'sancus.ca'
tests = [
	{
		'WebsiteName': 'http-mx service',
		'WebsiteURL': 'https://mx.{0}/dns/mx/google.com'.format(domain),
		'TestID': '1909311',
		'TestType': 'HTTP',
		'CheckRate': '300',
		'ContactGroup': '63464',
	},
	{
		'WebsiteName': 'broker get-email-account service',
		'WebsiteURL': 'https://broker.{0}/provider/list'.format(domain),
		'TestID': '1909320',
		'TestType': 'HTTP',
		'CheckRate': '300',
		'ContactGroup': '63464',
	},
	{
		'WebsiteName': 'autoconfig',
		'WebsiteURL': 'https://autoconfig.{0}/v1.1/'.format(domain),
		'TestID': '1909325',
		'TestType': 'HTTP',
		'CheckRate': '300',
		'ContactGroup': '63464',
	},
]

live_tests = [
	{
		'WebsiteName': 'live start redirect',
		'WebsiteURL': 'https://live.{0}/thunderbird/start'.format(domain),
		'TestID': '1909326',
		'TestType': 'HTTP',
		'CheckRate': '300',
		'ContactGroup': '63464',
	},
	{
		'WebsiteName': 'live firstrun redirect',
		'WebsiteURL': 'https://live.{0}/thunderbird/firstrun'.format(domain),
		'TestID': '1909330',
		'TestType': 'HTTP',
		'CheckRate': '300',
		'ContactGroup': '63464',
	},
]
