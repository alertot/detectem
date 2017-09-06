import sys
import json

try:
    import bottle
    from bottle import run, post, request
except ImportError:
    print('[+] Install bottle to use the web service')
    sys.exit(0)

from detectem.exceptions import SplashError, NoPluginsError
from detectem.cli import get_detection_results
from detectem.settings import DEBUG, SPLASH_TIMEOUT


@post('/detect')
def do_detection():
    url = request.forms.get('url')
    metadata = request.forms.get('metadata')

    metadata = bool(metadata == '1')

    try:
        result = get_detection_results(
            url, timeout=SPLASH_TIMEOUT, metadata=metadata
        )
    except (SplashError, NoPluginsError) as e:
        result = {'error': e.msg}

    return json.dumps(result)


def main():
    bottle.debug(DEBUG)
    run(host='0.0.0.0', port=5723)


if __name__ == '__main__':
    main()
