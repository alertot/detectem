import hashlib
import json
import logging
import pprint
import time

from contextlib import contextmanager

import docker
import requests

from detectem.exceptions import DockerStartError
from detectem.settings import (
    CMD_OUTPUT,
    DOCKER_SPLASH_IMAGE,
    JSON_OUTPUT,
    SETUP_SPLASH,
    SPLASH_MAX_TIMEOUT,
    SPLASH_URL,
)

logger = logging.getLogger("detectem")


def get_most_complete_pm(pms):
    """ Return plugin match with longer version, if not available
        will return plugin match with ``presence=True``
    """
    if not pms:
        return None

    selected_version = None
    selected_presence = None

    for pm in pms:
        if pm.version:
            if not selected_version:
                selected_version = pm
            else:
                if len(pm.version) > len(selected_version.version):
                    selected_version = pm
        elif pm.presence:
            selected_presence = pm

    return selected_version or selected_presence


def docker_error(method):
    def run_method(self=None):
        try:
            method(self)
        except docker.errors.DockerException as e:
            raise DockerStartError(f"Docker error: {e}")

    return run_method


class DockerManager:
    """
    Wraps requests to Docker daemon to manage Splash container.
    """

    def __init__(self):
        try:
            self.docker_cli = docker.from_env(version="auto")
            self.container_name = "splash-detectem"
        except docker.errors.DockerException:
            raise DockerStartError(
                "Could not connect to Docker daemon. "
                "Please ensure Docker is running."
            )

    def _get_splash_args(self):
        return f"--max-timeout {SPLASH_MAX_TIMEOUT}"

    def _get_container(self):
        try:
            return self.docker_cli.containers.get(self.container_name)
        except docker.errors.NotFound:
            try:
                return self.docker_cli.containers.create(
                    name=self.container_name,
                    image=DOCKER_SPLASH_IMAGE,
                    ports={
                        "5023/tcp": ("127.0.0.1", 5023),
                        "8050/tcp": ("127.0.0.1", 8050),
                        "8051/tcp": ("127.0.0.1", 8051),
                    },
                    command=self._get_splash_args(),
                )
            except docker.errors.ImageNotFound:
                raise DockerStartError(
                    f"Docker image {DOCKER_SPLASH_IMAGE} not found."
                    f"Please install it or set an image "
                    f"using DOCKER_SPLASH_IMAGE environment variable."
                )

    @docker_error
    def start_container(self):
        container = self._get_container()
        if container.status != "running":
            try:
                container.start()
                self._wait_container()
            except docker.errors.APIError as e:
                raise DockerStartError(
                    f"There was an error running Splash container: {e.explanation}"
                )

    def _wait_container(self):
        for t in [1, 2, 4, 6, 8, 10]:
            try:
                requests.get(f"{SPLASH_URL}/_ping")
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
        requests.post(f"{SPLASH_URL}/_gc")
    except requests.exceptions.RequestException:
        pass

    yield


def create_printer(oformat):
    if oformat == CMD_OUTPUT:
        return pprint.pprint
    elif oformat == JSON_OUTPUT:

        def json_printer(data):
            print(json.dumps(data))

        return json_printer


def get_url(entry):
    """ Return URL from response if it was received otherwise requested URL. """
    try:
        return entry["response"]["url"]
    except KeyError:
        return entry["request"]["url"]


def get_response_body(entry):
    return entry["response"]["content"]["text"]


def get_version_via_file_hashes(plugin, entry):
    file_hashes = getattr(plugin, "file_hashes", {})
    if not file_hashes:
        return

    url = get_url(entry)
    body = get_response_body(entry).encode("utf-8")
    for file, hash_dict in file_hashes.items():
        if file not in url:
            continue

        m = hashlib.sha256()
        m.update(body)
        h = m.hexdigest()

        for version, version_hash in hash_dict.items():
            if h == version_hash:
                return version
