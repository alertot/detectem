import logging
import sys
import click

from detectem.response import get_response
from detectem.plugin import load_plugins
from detectem.core import Detector
from detectem.exceptions import DockerStartError, SplashError, NoPluginsError
from detectem.utils import create_printer
from detectem.settings import SPLASH_TIMEOUT, CMD_OUTPUT, JSON_OUTPUT

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
    '--timeout',
    default=SPLASH_TIMEOUT,
    type=click.INT,
    help='Timeout for Splash (in seconds).'
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
def main(debug, timeout, format, metadata, url):
    if debug:
        click.echo("[+] Enabling debug mode.")
        ch.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.ERROR)

    printer = create_printer(format)
    try:
        results = get_detection_results(url, timeout, metadata)
    except (NoPluginsError, DockerStartError, SplashError) as e:
        printer(str(e))
        sys.exit(1)

    printer(results)


def get_detection_results(url, timeout, metadata):
    """ Return results from detector.

    This function prepares the environment loading the plugins,
    getting the response and passing it to the detector.

    In case of errors, it raises exceptions to be handled externally.

    """
    plugins = load_plugins()
    if not plugins:
        raise NoPluginsError('No plugins found')

    logger.debug('[+] Starting detection with %(n)d plugins', {'n': len(plugins)})

    response = get_response(url, plugins, timeout)
    det = Detector(response, plugins, url)
    results = det.get_results(metadata=metadata)

    return results


if __name__ == "__main__":
    main()
