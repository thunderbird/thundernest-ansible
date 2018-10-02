import sys
sys.path.append('/home/ansibler/thunderbird-website/')

import CloudFlare
import os
import settings

# these need to be in the environment
apikey = os.environ['CF_KEY']
email = os.environ['CF_EMAIL']
zone = os.environ['CF_ZONE_IDENTIFIER']

# Build URL list
tb = 'https://www.thunderbird.net/'
d = {'files': []}

for lang in settings.PROD_LANGUAGES:
    d['files'].append(tb+lang+'/')

d['files'].append('https://www.thunderbird.net/en-US/thunderbird/releases/')
d['files'].append('https://www.thunderbird.net/en-US/thunderbird/all/')
d['files'].append('https://www.thunderbird.net/media/js/common-bundle.js')

cf = CloudFlare.CloudFlare(email=email, token=apikey)
a = cf.zones.purge_cache.post(zone, data=d)
print a
