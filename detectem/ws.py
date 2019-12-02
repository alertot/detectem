import json
import sys

from detectem.cli import get_detection_results
from detectem.exceptions import NoPluginsError, SplashError
from detectem.settings import DEBUG, SPLASH_TIMEOUT

try:
    import bottle
    from bottle import run, post, request
except ImportError:
    print("[+] Install bottle to use the web service")
    sys.exit(0)


@post("/detect")
def do_detection():
    # Url is mandatory
    url = request.forms.get("url")
    if not url:
        return json.dumps({"error": "You must provide `url` parameter."})

    # metadata is optional
    metadata = request.forms.get("metadata", "0")
    metadata = bool(metadata == "1")

    # timeout is optional
    timeout = request.forms.get("timeout", type=int)
    if not timeout:
        timeout = SPLASH_TIMEOUT

    try:
        result = get_detection_results(url, timeout=timeout, metadata=metadata)
    except (SplashError, NoPluginsError) as e:
        result = {"error": e.msg}

    return json.dumps(result)


def main():
    bottle.debug(DEBUG)
    run(host="0.0.0.0", port=5723)


if __name__ == "__main__":
    main()
