import sys
import json

from detectem.exceptions import SplashError, NoPluginsError

try:
    from bottle import run, post, request
except ImportError:
    print("Install bottle to use the web service ..")
    sys.exit(0)


from detectem.cli import get_detection_results


@post('/detect')
def do_detection():
    url = request.forms.get('url')
    metadata = request.forms.get('metadata')

    metadata = bool(metadata == '1')

    try:
        result = get_detection_results(url, metadata=metadata)
    except (SplashError, NoPluginsError) as e:
        result = {'error': e}

    return json.dumps(result)


run(host='0.0.0.0', port=5723)
