import logging
import sys
import json
import click

from detectem.response import get_response
from detectem.plugin import load_plugins
from detectem.core import Detector
from detectem.exceptions import SplashError
from detectem.utils import print_error_message

# Set up logging
logger = logging.getLogger('detectem')
ch = logging.StreamHandler()
logger.setLevel(logging.ERROR)
logger.addHandler(ch)


@click.command()
@click.option(
    '--debug',
    default=False,
    is_flag=True,
    help='Include this flag to enable debug messages.'
)
@click.option(
    '--format',
    default=None,
    type=click.Choice(['json']),
    help='Set the format of the results.'
)
@click.option(
    '--metadata',
    default=False,
    is_flag=True,
    help='Include this flag to return plugin metadata.'
)
@click.argument('url')
def main(debug, format, metadata, url):
    if debug:
        click.echo("[+] Enabling debug mode.")
        ch.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.ERROR)

    print(get_detection_results(url, format, metadata))


def get_detection_results(url, format, metadata):
    plugins = load_plugins()
    logger.debug('[+] Starting detection with %(n)d plugins', {'n': len(plugins)})

    try:
        response = get_response(url, plugins)
    except SplashError as e:
        error_dict = {'error': 'Splash error: {}'.format(e)}
        print_error_message(error_dict, format=format)
        sys.exit(0)

    det = Detector(response, plugins, url)
    results = det.get_results(metadata=metadata)

    if format == 'json':
        return json.dumps(results)
    else:
        return results


if __name__ == "__main__":
    main()
