import logging

import click

from detectem.response import get_response
from detectem.plugin import load_plugins
from detectem.core import Detector

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

    response = get_response(url, plugins)
    det = Detector(response, plugins, url)
    det.start_detection()

    return det.get_results(format=format, metadata=metadata)


if __name__ == "__main__":
    main()
