import logging
import sys
import click

from operator import attrgetter

from detectem.response import get_response
from detectem.plugin import load_plugins
from detectem.core import Detector
from detectem.exceptions import DockerStartError, SplashError, NoPluginsError
from detectem.utils import create_printer
from detectem.settings import SPLASH_TIMEOUT, CMD_OUTPUT, JSON_OUTPUT


DUMMY_URL = "http://domain.tld"

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
@click.option(
    '--plugins', 'list_plugins',
    default=False,
    is_flag=True,
    help='List registered plugins'
)
@click.argument('url', default=DUMMY_URL, required=True)
def main(debug, timeout, format, metadata, list_plugins, url):
    if not list_plugins and url == DUMMY_URL:
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    if debug:
        click.echo("[+] Enabling debug mode.")
        ch.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.ERROR)

    printer = create_printer(format)
    try:
        if not list_plugins:
            results = get_detection_results(url, timeout, metadata)
        else:
            results = get_plugins(metadata)
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


def get_plugins(metadata):
    """ Return the registered plugins.

    Load and return all registered plugins.
    """
    plugins = load_plugins()
    if not plugins:
        raise NoPluginsError('No plugins found')

    results = []
    for p in sorted(plugins.get_all(), key=attrgetter('name')):
        if metadata:
            data = {'name': p.name, 'homepage': p.homepage}
            hints = getattr(p, 'hints', [])
            if hints:
                data['hints'] = hints
            results.append(data)
        else:
            results.append(p.name)
    return results


if __name__ == "__main__":
    main()
