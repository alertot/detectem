import json
import logging
import sys
import tempfile
from collections import namedtuple
from multiprocessing import Process, Queue, current_process
from operator import attrgetter
from urllib.parse import urlparse

import click
import click_log

from detectem.core import Detector
from detectem.exceptions import DockerStartError, NoPluginsError, SplashError
from detectem.plugin import load_plugins
from detectem.response import get_response
from detectem.settings import (
    CMD_OUTPUT,
    JSON_OUTPUT,
    NUMBER_OF_SPLASH_INSTANCES,
    SPLASH_MAX_RETRIES,
    SPLASH_TIMEOUT,
)
from detectem.splash import get_splash_manager
from detectem.utils import create_printer

# Set up logging
logger = logging.getLogger("detectem")
click_log.ColorFormatter.colors["info"] = dict(fg="green")
click_log.basic_config(logger)


TaskItem = namedtuple("TaskItem", ["args", "retries"])


@click.command()
@click.option(
    "--timeout",
    default=SPLASH_TIMEOUT,
    type=click.INT,
    help="Timeout for Splash (in seconds).",
)
@click.option(
    "--format",
    default=CMD_OUTPUT,
    type=click.Choice([CMD_OUTPUT, JSON_OUTPUT]),
    help="Set the format of the results.",
)
@click.option(
    "--metadata",
    default=False,
    is_flag=True,
    help="Include this flag to return plugin metadata.",
)
@click.option("--list-plugins", is_flag=True, help="List registered plugins")
@click.option("--save-har", is_flag=True, help="Save har to file")
@click.option("-i", "--input-file", type=click.File("r"), help="Read URLs from file")
@click_log.simple_verbosity_option(logger, default="error")
@click.argument("input_url", required=False)
def main(timeout, format, metadata, list_plugins, save_har, input_file, input_url):
    # Gather urls
    urls = []
    if input_file:
        urls += input_file.read().splitlines()
    if input_url:
        urls.append(input_url)

    # Check that `urls` contains valid URLs
    if not all(map(lambda u: urlparse(u).scheme in ["http", "https"], urls)):
        raise click.BadParameter("Check that all provided URLs are valid URLS")

    OPTIONS_WITHOUT_URLS = [list_plugins]

    # Exit if neither urls were defined nor an option that works without urls
    if not urls and not any(OPTIONS_WITHOUT_URLS):
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    printer = create_printer(format)

    # --list-plugins option
    if list_plugins:
        try:
            printer(get_plugins(metadata))
        except NoPluginsError as e:
            printer(str(e))
        finally:
            sys.exit(1)

    # Create queues
    task_queue = Queue()
    result_queue = Queue()

    # Init splash manager
    splash_manager = get_splash_manager()
    logger.info(f"[+] Using {splash_manager.__class__.__name__} as Splash manager")

    # Change number of instances if there are fewer urls to analyze
    n_instances = NUMBER_OF_SPLASH_INSTANCES
    if n_instances > len(urls):
        n_instances = len(urls)

    logger.info(f"[+] Using {n_instances} Splash instances")
    logger.info(f"[+] Setting up Splash manager")
    splash_manager.setup(n_instances)
    logger.info(f"[+] Setting up done")

    # Create pool of workers
    processes = [
        Process(
            target=process_url_worker,
            args=(splash_manager, task_queue, result_queue),
        )
        for _ in range(n_instances)
    ]

    # Start the workers
    for p in processes:
        p.start()

    # Send the provided urls to the input queue
    for url in urls:
        task_queue.put(TaskItem(args=[url, timeout, metadata, save_har], retries=0))

    # Wait until processing on all workers is done
    for p in processes:
        p.join()

    # Process results
    results = []
    while not result_queue.empty():
        result = result_queue.get()
        results.append(result)

    printer(results)

    splash_manager.teardown()


def process_url_worker(splash_manager, task_queue, result_queue):
    process_name = current_process().name

    with splash_manager.sem:
        task_item: TaskItem

        for task_item in iter(task_queue.get, "STOP"):
            args = task_item.args
            url = args[0]

            # Get a Splash instance from pool of Splash servers
            with splash_manager.assign_instance() as (container_name, splash_url):
                result = None

                logger.info(
                    f"[+] Processing {url} @ {process_name} [retry: {task_item.retries} | instance: {container_name}]"
                )

                try:
                    result = get_detection_results(*args + [splash_url])
                except SplashError as e:
                    # Handle limit of retries
                    retries = task_item.retries + 1

                    if retries == SPLASH_MAX_RETRIES:
                        result = {
                            "url": url,
                            "error": "Maximum number of retries reached.",
                        }
                    else:
                        # Put back in `task_queue` with incremented `retries`
                        task_queue.put(TaskItem(args=task_item.args, retries=retries))

                        # Notify error to the manager
                        if splash_manager.handles_errors:
                            splash_manager.handle_error(container_name)
                except (NoPluginsError, DockerStartError) as e:
                    result = {"url": url, "error": str(e)}

                if result:
                    result_queue.put(result)

                # Finish if there aren't any more tasks in the queue
                if task_queue.empty():
                    logger.info(f"[+] Processing is done @ {process_name}")
                    return


def get_detection_results(
    url,
    timeout,
    metadata=False,
    save_har=False,
    splash_url="",
):
    """Return results from detector.

    This function prepares the environment loading the plugins,
    getting the response and passing it to the detector.

    In case of errors, it raises exceptions to be handled externally.

    """
    plugins = load_plugins()
    if not plugins:
        raise NoPluginsError("No plugins found")

    logger.debug("[+] Starting detection with %(n)d plugins", {"n": len(plugins)})

    response = get_response(url, plugins, timeout, splash_url)

    # Save HAR
    if save_har:
        fd, path = tempfile.mkstemp(suffix=".har")
        logger.info(f"Saving HAR file to {path}")

        with open(fd, "w") as f:
            json.dump(response["har"], f)

    det = Detector(response, plugins, url)
    softwares = det.get_results(metadata=metadata)

    output = {"url": url, "softwares": softwares}

    return output


def get_plugins(metadata):
    """Return the registered plugins.

    Load and return all registered plugins.
    """
    plugins = load_plugins()
    if not plugins:
        raise NoPluginsError("No plugins found")

    results = []
    for p in sorted(plugins.get_all(), key=attrgetter("name")):
        if metadata:
            data = {"name": p.name, "homepage": p.homepage}
            hints = getattr(p, "hints", [])
            if hints:
                data["hints"] = hints
            results.append(data)
        else:
            results.append(p.name)
    return results


if __name__ == "__main__":
    main()
