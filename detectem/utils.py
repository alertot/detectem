import re
import time
import logging
import json
import pprint

from contextlib import contextmanager

import docker
import requests

from detectem.exceptions import DockerStartError, NotNamedParameterFound
from detectem.settings import (
    SPLASH_URL, SETUP_SPLASH, DOCKER_SPLASH_IMAGE,
    SPLASH_MAX_TIMEOUT,
    JSON_OUTPUT, CMD_OUTPUT
)


logger = logging.getLogger('detectem')


def get_most_complete_version(versions):
    """ Return the most complete version.

    i.e. `versions=['1.4', '1.4.4']` it returns '1.4.4' since it's more complete.
    """
    if not versions:
        return

    return max(versions)


def check_presence(text, matchers):
    for matcher in matchers:
        if isinstance(matcher, str):
            v = re.search(matcher, text, flags=re.DOTALL)
            if v:
                return True
        elif callable(matcher):
            v = matcher(text)
            if v:
                return True

    return False


def extract_data(text, matchers, parameter):
    for matcher in matchers:
        if isinstance(matcher, str):
            v = re.search(matcher, text, flags=re.DOTALL)
            if v:
                try:
                    return v.group(parameter)
                except IndexError:
                    raise NotNamedParameterFound(
                        'Parameter %s not found in regexp' %
                        parameter
                    )
        elif callable(matcher):
            v = matcher(text)
            if v:
                return v


def extract_version(text, matchers):
    return extract_data(text, matchers, 'version')


def extract_name(text, matchers):
    return extract_data(text, matchers, 'name')


def extract_from_headers(headers, matchers, extraction_function):
    for matcher_name, matcher_value in matchers:
        for header in headers:
            if header['name'] == matcher_name:
                v = extraction_function(header['value'], [matcher_value])
                if v:
                    return v


def docker_error(method):
    def run_method(self=None):
        try:
            method(self)
        except docker.errors.DockerException as e:
            raise DockerStartError("Docker error: {}".format(e))
    return run_method


class DockerManager:
    """
    Wraps requests to Docker daemon to manage Splash container.
    """
    def __init__(self):
        try:
            self.docker_cli = docker.from_env(version='auto')
            self.container_name = 'splash-detectem'
        except docker.errors.DockerException:
            raise DockerStartError(
                "Could not connect to Docker daemon. "
                "Please ensure Docker is running."
            )

    def _get_splash_args(self):
        return '--max-timeout {}'.format(SPLASH_MAX_TIMEOUT)

    def _get_container(self):
        try:
            return self.docker_cli.containers.get(self.container_name)
        except docker.errors.NotFound:
            try:
                return self.docker_cli.containers.create(
                    name=self.container_name,
                    image=DOCKER_SPLASH_IMAGE,
                    ports={
                        '5023/tcp': 5023,
                        '8050/tcp': 8050,
                        '8051/tcp': 8051,
                    },
                    command=self._get_splash_args(),
                )
            except docker.errors.ImageNotFound:
                raise DockerStartError(
                    "Docker image {} not found. Please install it or set an image "
                    "using DOCKER_SPLASH_IMAGE environment variable."
                    .format(DOCKER_SPLASH_IMAGE)
                )

    @docker_error
    def start_container(self):
        container = self._get_container()
        if container.status != 'running':
            try:
                container.start()
                self._wait_container()
            except docker.errors.APIError as e:
                raise DockerStartError(
                    "There was an error running Splash container: {}"
                    .format(e.explanation)
                )

    def _wait_container(self):
        for t in [1, 2, 4, 6, 8, 10]:
            try:
                requests.get('{}/_ping'.format(SPLASH_URL))
                break
            except requests.exceptions.RequestException:
                time.sleep(t)
        else:
            raise DockerStartError(
                "Could not connect to started Splash container. "
                "See 'docker logs splash-detectem' for more details, "
                "or remove the container to try again."
            )


@contextmanager
def docker_container():
    """ Start the Splash server on a Docker container.
    If the container doesn't exist, it is created and named 'splash-detectem'.

    """
    if SETUP_SPLASH:
        dm = DockerManager()
        dm.start_container()

    try:
        requests.post('{}/_gc'.format(SPLASH_URL))
    except requests.exceptions.RequestException:
        pass

    yield


def create_printer(format):
    if format == CMD_OUTPUT:
        return pprint.pprint
    elif format == JSON_OUTPUT:
        def json_printer(data):
            print(json.dumps(data))
        return json_printer
