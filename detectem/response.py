import requests
import base64
import sys
import logging
import re
import pkg_resources
import json
import urllib.parse

from string import Template

from detectem.settings import SPLASH_URL
from detectem.exceptions import DockerStartError, SplashError
from detectem.utils import docker_container

DEFAULT_CHARSET = 'iso-8859-1'
ERROR_STATUS_CODES = [400, 504]

logger = logging.getLogger('detectem')


def is_url_allowed(url):
    """ Return ``True`` if ``url`` is not in ``blacklist``.

    :rtype: bool

    """
    blacklist = [
        '\.ttf', '\.woff', 'fonts\.googleapis\.com', '\.png', '\.jpe?g', '\.gif'
    ]

    for ft in blacklist:
        if re.search(ft, url):
            return False

    return True


def is_valid_mimetype(response):
    """ Return ``True`` if the mimetype no contains words from the blacklist.

    :rtype: bool

    """
    blacklist = [
        'image/',
    ]

    mimetype = response.get('mimeType')
    if not mimetype:
        return True

    for bw in blacklist:
        if bw in mimetype:
            return False

    return True


def get_charset(response):
    """ Return charset from ``response`` or default charset.

    :rtype: str

    """
    # Set default charset
    charset = DEFAULT_CHARSET

    m = re.findall(';charset=(.*)', response.get('mimeType', ''))
    if m:
        charset = m[0]

    return charset


def create_lua_script(plugins):
    """ Return script template filled up with plugin javascript data.

    :rtype: str

    """
    lua_template = pkg_resources.resource_string('detectem', 'script.lua')
    template = Template(lua_template.decode('utf-8'))

    javascript_data = [{'name': p.name, 'matchers': p.js_matchers}
                       for p in plugins.with_js_matchers()]

    return template.substitute(js_data=json.dumps(javascript_data))


def get_response(url, plugins):
    """ Return response with har and detected software. i

    :rtype: dict

    """
    lua_script = create_lua_script(plugins)
    lua = urllib.parse.quote_plus(lua_script)
    page_url = '{}/execute?url={}&lua_source={}'.format(SPLASH_URL, url, lua)

    try:
        with docker_container():
            logger.debug('[+] Sending request to Splash instance')
            res = requests.get(page_url)
    except DockerStartError:
        logger.error(
            "There was an error running splash container. "
            "It's possible that previous splash container didn't finish well, "
            "please verify and stop any other splash instance to avoid port issues."
        )
        sys.exit(0)

    logger.debug('[+] Response received')

    json_data = res.json()

    if res.status_code in ERROR_STATUS_CODES:
        raise SplashError(json_data['description'])

    softwares = json_data['softwares']
    har = get_valid_har(json_data['har'])

    logger.debug('[+] Detected %(n)d softwares from the DOM', {'n': len(softwares)})
    logger.debug('[+] Final HAR has %(n)d valid entries', {'n': len(har)})

    return {'har': har, 'softwares': softwares}


def get_valid_har(har_data):
    """ Return list of valid har entries.

    :rtype: list

    """
    new_entries = []
    entries = har_data.get('log', {}).get('entries', [])
    logger.debug('[+] Detected %(n)d entries in HAR', {'n': len(entries)})

    for entry in entries:
        url = entry['request']['url']
        if not is_url_allowed(url):
            continue

        response = entry['response']['content']
        if not is_valid_mimetype(response):
            continue

        # Some responses are empty, we delete them
        if not response.get('text'):
            continue

        charset = get_charset(response)
        response['text'] = base64.b64decode(response['text']).decode(charset)
        new_entries.append(entry)

        logger.debug('[+] Added URL: %(url)s ...', {'url': url[:100]})

    return new_entries
