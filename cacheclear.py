import sys
sys.path.append('/home/ansibler/thunderbird-website/')

import CloudFlare
import os
import settings

# these need to be in the environment
apikey = os.environ['CF_KEY']
email = os.environ['CF_EMAIL']
zone = os.environ['CF_ZONE_IDENTIFIER']

# Cloudflare has a 30-item limit on API cache purges now.
def chunks(lst, n):
    for i in xrange(0, len(lst), n):
        yield lst[i:i + n]

# Build URL list
tb = 'https://www.thunderbird.net/'
urls = []

for lang in settings.PROD_LANGUAGES:
    urls.append(tb+lang+'/')

urls.append('https://www.thunderbird.net/en-US/thunderbird/releases/')
urls.append('https://www.thunderbird.net/en-US/thunderbird/all/')
urls.append('https://www.thunderbird.net/media/js/common-bundle.js')

cf = CloudFlare.CloudFlare(email=email, token=apikey)

lists = chunks(urls, 30) # Split into 30-item requests.
for url_list in lists:
    # Put it in the format the API expects.
    api_req = {'files': url_list}

    a = cf.zones.purge_cache.post(zone, data=api_req)
    print a
print "Completed."
