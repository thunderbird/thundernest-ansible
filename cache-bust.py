import sys

sys.path.append('/home/ansibler/thunderbird-website/')

from CloudFlare import CloudFlare
import os

from git import Repo
import argparse as argparse

# these need to be in the environment
apikey = os.environ['CF_KEY']
email = os.environ['CF_EMAIL']
zone = os.environ['CF_ZONE_IDENTIFIER']

# Cloudflare has a 30-item limit on API cache purges now.
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def main():
    parser = argparse.ArgumentParser("Cache Buster", description="Cloudflare Cache Buster. By default it won't bust the cache unless you pass the `--bust-cache` argument.")
    parser.add_argument('path', help="Path to the git directory we're diffing.")
    parser.add_argument('--print-urls', action='store_true', help="Print each of the to-be-cache-busted url.")
    parser.add_argument('--bust-cache', action='store_true', help="Bust the CloudFlare cache.")
    args = parser.parse_args()

    path = args.path
    urls = gather_urls(path)

    if args.print_urls is True:
        print("Printing out urls:")
        for url in urls:
            print(url)

    if args.bust_cache is True:
        print("Busting cache for {} urls.".format(len(urls)))
        bust_cache(urls)

    print("Finished.")


def bust_cache(url_list):
    """ Talks with cloudflare to bust the requested urls """
    cf = CloudFlare(email=email, token=apikey)

    for urls in chunks(url_list, 30):
        api_req = {'files': urls}
        # See: https://developers.cloudflare.com/api/operations/zone-purge-files-by-cache-tags,-host,-or-prefix

        try:
            response = cf.zones.purge_cache.post(zone, data=api_req)
            print("Cloudflare Response: {}".format(response))
        except CloudFlare.exceptions.CloudFlareAPIError as err:
            # If there's any errors with busting the cache, then just stop doing it. Don't want to prevent the deployment.
            print("Error busting cache: {}".format(err))
            break

def gather_urls(repo_path):
    """ Gathers list of urls from the git diff. """
    # Grab the repo from
    repo = Repo(repo_path)
    # Diff against our previous commit
    diff = repo.head.commit.diff("HEAD~1")

    url_list = []

    for item in diff:
        # We can skip new files
        if item.change_type == 'A':
            continue

        # For deletes we want the path that existed prior to the deletion
        if item.change_type == 'D':
            path = item.a_path
        else:
            path = item.b_path

        # We're currently only busting thunderbird.net caches
        if path is None or not path.startswith("thunderbird.net"):
            continue

        # This will form https://www.thunderbird.net/ etc...
        url = "https://www.{}".format(path)

        # If it's an index page, remove the index.html
        if "index.html" in url:
            url = url.replace('index.html', '')

        url_list.append(url)

    return url_list

if __name__ == '__main__':
    main()