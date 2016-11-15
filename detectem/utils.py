import re
import time
import os

from contextlib import contextmanager

import docker

from detectem.exceptions import DockerStartError, NotVersionNamedParameterFound
from detectem.settings import DOCKER_SOCKET


def extract_version(text, matchers):
    for matcher in matchers:
        if isinstance(matcher, str):
            v = re.search(matcher, text, flags=re.DOTALL)
            if v:
                try:
                    return v.group('version')
                except IndexError:
                    raise NotVersionNamedParameterFound
        elif callable(matcher):
            v = matcher(text)
            if v:
                return v


def extract_version_from_headers(headers, matchers):
    for matcher_name, matcher_value in matchers:
        for header in headers:
            if header['name'] == matcher_name:
                v = extract_version(header['value'], [matcher_value])
                if v:
                    return v


@contextmanager
def docker_container():
    """ Setup and teardown docker container for doing requests
    It's a temporary implementation until cache managements is supported
    by splash.

    """
    if not os.path.exists(DOCKER_SOCKET):
        raise FileNotFoundError('DOCKER_SOCKET not found')

    docker_cli = docker.Client(base_url='unix:/{}'.format(DOCKER_SOCKET), version='auto')

    container = docker_cli.create_container(
        image='scrapinghub/splash',
        ports=[5023, 8050, 8051],
        host_config=docker_cli.create_host_config(
            port_bindings={5023: 5023, 8050: 8050, 8051: 8051}
        )
    )

    try:
        docker_cli.start(container['Id'])
    except docker.errors.APIError:
        raise DockerStartError

    # Wait to container to start
    time.sleep(1)

    yield

    # Container clean-up
    docker_cli.stop(container['Id'])
    docker_cli.remove_container(container['Id'])
