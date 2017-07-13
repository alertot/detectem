import logging
import sys
import json
import click
import pprint

from detectem.response import get_response
from detectem.plugin import load_plugins
from detectem.core import Detector
from detectem.exceptions import SplashError
from detectem.utils import print_error_message
from detectem.settings import CMD_OUTPUT, JSON_OUTPUT

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
    default=CMD_OUTPUT,
    type=click.Choice([CMD_OUTPUT, JSON_OUTPUT]),
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

    results = get_detection_results(url, format, metadata)
    if format == CMD_OUTPUT:
        pprint.pprint(results)
    elif format == JSON_OUTPUT:
        print(results)


def get_detection_results(url, format, metadata):
    plugins = load_plugins()
    if not plugins:
        error_dict = {'error': 'No plugins found in $DET_PLUGIN_PACKAGES'}
        print_error_message(error_dict, format=format)
        sys.exit(0)
    logger.debug('[+] Starting detection with %(n)d plugins', {'n': len(plugins)})

    try:
        response = get_response(url, plugins)
    except SplashError as e:
        error_dict = {'error': 'Splash error: {}'.format(e)}
        print_error_message(error_dict, format=format)
        sys.exit(0)

    det = Detector(response, plugins, url)
    results = det.get_results(metadata=metadata)

    if format == JSON_OUTPUT:
        return json.dumps(results)
    else:
        return results


if __name__ == "__main__":
    main()
