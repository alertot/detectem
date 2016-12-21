import sys

try:
    from bottle import run, post, request
except ImportError:
    print("Install bottle to use the web service ..")
    sys.exit(0)


from detectem.cli import get_detection_results


@post('/detect')
def do_detection():
    url = request.forms.get('url')
    return get_detection_results(url, format='json')


run(host='0.0.0.0', port=5723)
