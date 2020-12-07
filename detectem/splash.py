import abc
import logging
import multiprocessing
import time
from contextlib import contextmanager
from typing import Callable, Iterator, Optional

import docker
import requests
from docker.client import DockerClient
from docker.models.containers import Container

from detectem.exceptions import DockerStartError
from detectem.settings import (
    DOCKER_SPLASH_IMAGE,
    NUMBER_OF_SPLASH_INSTANCES,
    SETUP_SPLASH,
    SPLASH_MAX_TIMEOUT,
    SPLASH_URLS,
)

logger = logging.getLogger("detectem")


class SplashManagerInterface(abc.ABC):
    handles_errors = True

    def __init__(self, *args, **kwargs):
        self.manager = multiprocessing.Manager()
        self.lock = multiprocessing.Lock()
        self.sem = multiprocessing.Semaphore(NUMBER_OF_SPLASH_INSTANCES)

        # State
        self._instances = self.manager.dict()

    def get_number_of_available_instances(self):
        return len(self._instances)

    @abc.abstractmethod
    def setup(self, n_instances: int):
        ...

    @abc.abstractmethod
    def teardown(self):
        ...

    @abc.abstractmethod
    def handle_error(self, instance_name: str):
        ...

    @contextmanager
    def assign_instance(self) -> Iterator:
        """Context manager that gets a not "in use" Splash instance,
        sets it as "in use" to not be used by any other process,
        requests the instance HTTP endpoint to run the garbage collector,
        yields a tuple `(instance_name, instance_url)` to be used in code
        and then sets the instance as not "in use".

        """
        instance_name: str = ""
        instance_data: dict = {}

        with self.lock:
            for instance_name, instance_data in self._instances.items():
                if instance_data["in_use"]:
                    continue

                # Set instance in use and update it in multiprocessing's way
                instance_data["in_use"] = True
                self._instances[instance_name] = instance_data

                break

        # Get Splash url and clean container (call garbage collector)
        url: str = instance_data["url"]
        try:
            requests.post(f"{url}/_gc")
        except requests.exceptions.RequestException:
            pass

        yield (instance_name, url)

        # Set container as not in use
        with self.lock:
            # Update dict multiprocessing's way
            instance_data = self._instances[instance_name]
            instance_data["in_use"] = False
            self._instances[instance_name] = instance_data


class RemoteSplashManager(SplashManagerInterface):
    handles_errors = False

    def __init__(self, *args, **kwargs):
        if NUMBER_OF_SPLASH_INSTANCES != len(SPLASH_URLS):
            raise ValueError(
                "Number of Splash instances must match number of provided Splash urls"
            )

        super().__init__(*args, **kwargs)

    def setup(self, n_instances):
        for index, url in enumerate(SPLASH_URLS):
            name = f"instance-{index}"
            self._instances[name] = {
                "url": url,
                "in_use": False,
            }

    def teardown(self):
        # Nothing to do
        pass

    def handle_error(self, instance_name: str):
        # Nothing to do
        pass


def docker_error(method: Callable):
    """ Decorator to catch docker exceptions """

    def run_method(*args, **kwargs):
        try:
            method(*args, **kwargs)
        except docker.errors.DockerException as e:
            raise DockerStartError(f"Docker error: {e}")

    return run_method


class DockerSplashManager(SplashManagerInterface):
    """ Manage Splash instances using local docker """

    MAXIMUM_NUMBER_OF_ERRORS = 3

    _docker_cli: Optional[DockerClient] = None

    @property
    def docker_cli(self) -> DockerClient:
        """Return a docker client instance

        Raises:
            - DockerError
        """
        if not self._docker_cli:
            try:
                self._docker_cli: DockerClient = docker.from_env(version="auto")
            except docker.errors.DockerException:
                raise DockerStartError(
                    "Could not connect to Docker daemon. "
                    "Please ensure Docker is running and your user has access."
                )

        return self._docker_cli

    def _wait_container(self, container_name):
        """ Wait until Splash HTTP service is ready to receive requests """
        url = self._instances[container_name]["url"]

        for t in [1, 2, 4, 6, 8, 10]:
            try:
                requests.get(f"{url}/_ping")
                break
            except requests.exceptions.RequestException:
                time.sleep(t)
        else:
            raise DockerStartError(
                f"Could not connect to started Splash container. "
                f"See 'docker logs {container_name}' for more details."
            )

    @docker_error
    def setup(self, n_instances: int):
        """Fill ``self._instances`` with created containers.

        ``n_instances`` could be equal to NUMBER_OF_SPLASH_INSTANCES or lower
        since it's also determined by the number of URLs to analyze.

        It also checks that the target docker image exists
        and there weren't any issues creating the containers.

        """
        # Check base image
        try:
            self.docker_cli.images.get(DOCKER_SPLASH_IMAGE)
        except docker.errors.ImageNotFound:
            raise DockerStartError(
                f"Docker image {DOCKER_SPLASH_IMAGE} not found."
                f"Please install it or set an image using DOCKER_SPLASH_IMAGE environment variable."
            )

        for container_index in range(n_instances):
            container_name = f"splash-detectem-{container_index}"
            port = 8050 + container_index

            self._instances[container_name] = {
                "url": f"http://localhost:{port}",
                "in_use": False,
                "errors": 0,
            }

            try:
                container: Container = self.docker_cli.containers.get(container_name)
            except docker.errors.NotFound:
                # If not found, create it
                container: Container = self.docker_cli.containers.create(
                    name=container_name,
                    image=DOCKER_SPLASH_IMAGE,
                    ports={
                        "8050/tcp": ("127.0.0.1", port),
                    },
                    command=f"--max-timeout {SPLASH_MAX_TIMEOUT}",
                )

            if container.status != "running":
                container.start()

                try:
                    self._wait_container(container_name)
                except DockerStartError:
                    # If the container didn't start it's probable to be a unrecuperable error
                    # We stop it and delete the container to be recreated next run
                    container.stop()
                    container.remove()
                    # Also it's not available to send work to
                    del self._instances[container_name]
                    continue

    @docker_error
    def teardown(self):
        for container_name in self._instances:
            container: Container = self.docker_cli.containers.get(container_name)
            container.stop()

    @docker_error
    def handle_error(self, container_name: str):
        with self.lock:
            # Update dict multiprocessing's way
            instance_data = self._instances[container_name]
            instance_data["errors"] += 1
            self._instances[container_name] = instance_data

        if instance_data["errors"] >= self.MAXIMUM_NUMBER_OF_ERRORS:
            logger.warning(
                f"[-] Restarting container {container_name} due to errors .."
            )

            container: Container = self.docker_cli.containers.get(container_name)
            container.restart()
            self._wait_container(container_name)

            # Restart error counter
            with self.lock:
                # Update dict multiprocessing's way
                instance_data = self._instances[container_name]
                instance_data["errors"] = 0
                self._instances[container_name] = instance_data


def get_splash_manager() -> SplashManagerInterface:
    if SETUP_SPLASH:
        return DockerSplashManager()

    return RemoteSplashManager()
