import requests
import base64
import sys
import logging
import re

from detectem.settings import SPLASH_URL
from detectem.exceptions import DockerStartError
from detectem.utils import docker_container

logger = logging.getLogger('detectem')


def is_url_allowed(url, blacklist):
    for ft in blacklist:
        ft = re.escape(ft)
        if re.search(ft, url):
            return False

    return True


def get_har(url):
    page_url = '{}/render.har?url={}&response_body=1&wait=3&images=0'.format(
        SPLASH_URL, url
    )

    try:
        with docker_container():
            res = requests.get(page_url)
    except DockerStartError:
        logger.error(
            "There was an error running splash container. "
            "It's possible that previous splash container didn't finish well, "
            "please verify and stop any other splash instance to avoid port issues."
        )
        sys.exit(0)

    json_data = res.json()
    entries = json_data.get('log', {}).get('entries', [])
    blacklist = ['.ttf', '.woff', 'fonts.googleapis.com']

    logger.debug('[+] Detected %(n)d entries in HAR.', {'n': len(entries)})

    new_entries = []
    for entry in entries:
        url = response = entry['request']['url']
        if not is_url_allowed(url, blacklist):
            continue

        response = entry['response']['content']

        # Some responses are empty, we delete them
        if not response.get('text'):
            continue

        response['text'] = str(base64.b64decode(response['text']))
        new_entries.append(entry)

        logger.debug('[+] Added URL: %(url)s ...', {'url': url[:100]})

    return new_entries
