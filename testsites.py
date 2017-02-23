import requests
ignore_headers = set(['x-cache-info', 'connection', 'server', 'x-powered-by', 'x-backend-server'])

live = {'moz': 'live.mozillamessaging.com',
		'tb': 'live.sancus.ca'
}

broker = {'moz': 'broker.thunderbird.net',
		'tb': 'broker-live.sancus.ca'
}

mx = {'moz': 'mx.thunderbird.net',
		'tb': 'mx.sancus.ca'
}

autoconfig = {'moz': 'autoconfig.thunderbird.net',
		'tb': 'autoconfig.sancus.ca'
}


live_urls = [
'/thunderbird/start/?locale=en-US&version=52&os=WINNT&buildid=20170206074256',
'/thunderbird/releasenotes/?locale=en-US&version=45.7.1&os=WINNT&buildid=20170206074256/',
'/thunderbird/firstrun/?locale=en-US&version=45.7.1&os=WINNT&buildid=20170206074256/',
'/thunderbird/whatsnew/?locale=en-US&version=45.7.1&os=WINNT&buildid=20170206074256/',
'/thunderbird/plugin-crashed/?locale=en-US&version=45.7.1&os=WINNT&buildid=20170206074256/',
'/thunderbird/addons/search?q=header&locale=en-US&lver=45.7.1&hver=45.7.1&os=WINNT',
]

mx_urls = [
'/dns/mx/google.com',
'/dns/mx/garbagegoeshere',
'/dns/mx/doesntexistatall345354345345345.com',
'/dns/mx/mozilla.com',
]

autoconfig_urls = [
'/v1.1/',
'/v1.0/',
'/v1.0/1and1.com',
'/v1.1/2die4.com',
]

broker_urls = [
'/provider/list',
'/provider/suggest?first_name=andrei&last_name=hajdukewycz&providers=gandi',
'/provider/suggest?totalgarbage=lol',
'/provider/suggest?first_name=andrei',
]

class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect
    def removed(self):
        return self.set_past - self.intersect
    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])

def header_diff(moz, tb):
	diff = DictDiffer(moz, tb)

	changed = diff.changed() - ignore_headers
	added = diff.added() - ignore_headers
	removed = diff.removed() - ignore_headers

	if len(changed) > 0:
		print "Headers Changed"
		for i in changed:
			print i + ": Moz:" + moz.get(i, 'EMPTY') + "|" + tb.get(i, 'EMPTY')
	if len(added) > 0:
		print "Headers Added"
		for i in added:
			print i + ":" + tb.get(i, 'EMPTY')
	if len(removed) > 0:
		print "Headers Removed"
		for i in removed:
			print i

def checkurls(domains, urls):
	print "------------------------------------------Testing {0}--------------------------------------------".format(domains['moz'])
	for url in urls:
		moztarget = "https://" + domains['moz'] + url
		tbtarget = "https://" + domains['tb'] + url
		moz = requests.get(moztarget, allow_redirects=False)
		tb = requests.get(tbtarget, allow_redirects=False)

		if moz.status_code == tb.status_code and (moz.status_code == 301 or moz.status_code == 302):
			mozh = moz.headers
			tbh = tb.headers
			moz = requests.get(moztarget)
			tb = requests.get(moztarget)
			if moz.url == tb.url:
				print "Match for REDIRECT %s" % url
				#header_diff(mozh, tbh)
		else:
			if tb.text == moz.text and tb.status_code == moz.status_code:
				print "Match for %s" % url
			else:
				print "Error for %s" % url
				print tb.text
				print moz.text
			#header_diff(moz.headers, tb.headers)

checkurls(mx, mx_urls)
checkurls(broker, broker_urls)
checkurls(live, live_urls)
checkurls(autoconfig, autoconfig_urls)
